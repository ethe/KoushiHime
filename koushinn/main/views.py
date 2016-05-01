# -*- coding: utf-8 -*-

from datetime import datetime
from flask.views import MethodView
from flask.ext.login import current_user, login_required
from flask.ext.paginate import Pagination as PaginationBar
from flask import render_template, redirect, url_for, request, jsonify, flash, current_app, abort
from koushinn.auth.models import UserOperation, User, Role
from koushinn.auth.constants import Permission, Operation
from koushinn.utils import Pagination, admin_required
from koushinn.utils.moegirl import MoegirlQuery
from utils import recent_have_pushed, have_auto_catched
from models import WaitingList, BanList
from form import PushForm, AddUserForm, EditProfileForm, AdminEditProfileForm, BanKeywordForm


class Index(MethodView):

    def get(self):
        if not current_user:
            return redirect(url_for("auth.login"))
        return render_template('index.html')


class Update(MethodView):
    decorators = [login_required]

    def get(self, page):
        per_page = 10
        unpushed_entry = WaitingList.query.order_by(WaitingList.id).all()
        pagination = Pagination(unpushed_entry, per_page)
        current_page = pagination.page(page)
        foot_bar = PaginationBar(css_framework='bootstrap3', link_size='sm',
                                 show_single_page=False, page=page,
                                 per_page=per_page, total=pagination.pages_num,
                                 format_total=True, format_number=True)
        result = {
            "titles": current_page,
            "current_time": datetime.utcnow(),
            "pushtime": 10,
            "deltime": 999,
            "page": page,
            "per_page": per_page,
            "pagination": foot_bar
        }
        return render_template('update.html', **result)

    def post(self, page):
        data = request.get_json()
        if data['action'] == 'post':
            title = data["title"]
            current_weight = current_app.config["CUTTING_WEIGHT_INIT"]
            entry = WaitingList.query.filter_by(title=title).first()
            if entry:
                entry.cutting_weight = current_weight + 1  # FIXME: 即使条目处于权重最高状态亦可增加权限
                entry.save()
                current_app.config["CUTTING_WEIGHT_INIT"] += 1
        elif data['action'] == 'del':
            title = data['title']
            UserOperation(user_id=current_user.id, operation=Operation.DELETE, title=title).save()
            query = WaitingList.query.filter_by(title=data['title']).first()
            if query:
                query.delete()
        response = jsonify({'result': True})
        return response


class ManualUpdate(MethodView):
    decorators = [login_required]

    def __init__(self):
        self.form = PushForm

    def get(self):
        return render_template('mupdate.html', form=self.form(), pushtime=10)

    def post(self):
        if current_user.can(Permission.MANUEL_PUSH):
            form = self.form(request.form)
            if form.validate():
                title = form.pushtitle.data
                result = self.check_push_validate(title)
                if result:
                    WaitingList(title=title).save()
                    UserOperation(user_id=current_user.id, title=title).save()
                    flash(u"操作成功，词条将在下一次推送中推送")
                else:
                    flash(u"推送条目被ban，或者已经在24小时之内推送过，或者已经被更新姬捕捉进精灵球")
            else:
                flash(u"条目格式有问题，请检查并重新填写")
        else:
            flash(u"你没有权限")
            return redirect(url_for('main.mupdate'))

    @staticmethod
    def check_push_validate(title):
        moegirl_entry = MoegirlQuery(title)
        namespace = moegirl_entry.get_namespace()
        if namespace is 0:
            baned_from_moegirl = moegirl_entry.banned_moegirl_category()
            has_pushed = recent_have_pushed(title)  # TODO: 改成自动冒泡
            has_catched = have_auto_catched(title)
            # TODO: 推送检查是否被正则ban掉
            result = baned_from_moegirl is False and has_pushed is False and has_catched is False
            return result
        else:
            return False


class UserInfo(MethodView):
    decorators = [login_required]

    def get(self, username):
        is_admin = current_user.can(Permission.ADMINISTER)
        if current_user.username == username or is_admin is True:
            user_info = User.query.query.filter_by(username=username, delete=False).first()
            if not user_info:
                abort(404)
            return render_template('user.html', u=user_info, username=user_info.username)
        else:
            abort(403)


class UserList(MethodView):
    decorators = [login_required, admin_required]

    def __init__(self):
        self.form = AddUserForm

    def get(self):
        userlist = User.query.filter_by(delete=False).all()
        return render_template('userlist.html', userlist=userlist, form=self.form())

    def post(self):
        data = request.get_json()
        if data:
            if data['action'] == 'edit':
                username = data['username']
                return redirect(url_for('main.editprofile'), username=username)
            else:
                username = data['username']
                try:
                    User.query.filter_by(username=username, delete=False).first().delete()
                except:
                    flash(u'用户不存在')
        elif request.form:
            self.add_user()
        return redirect('userlist')

    def add_user(self):
        form = self.form(request.form)
        if form.validate():
            role = Role.query.filter_by(name=form.role.data).first()
            if role:
                if not User.query.filter_by(email=form.email.data).exists():
                    user = User(email=form.email.data, username=form.username.data,
                                role=role, password=form.password.data)
                    user.save()
                else:
                    flash(u'已经存在该用户')
            else:
                flash(u'不存在该用户组')
        return redirect(url_for('main.userlist'))


class EditProfile(MethodView):
    decorators = [login_required]

    def __init__(self):
        self.form = EditProfileForm
        self.admin_form = AdminEditProfileForm

    def get(self, username):
        if not username:  # 用户访问自己的个人信息编辑页
            user_info = current_user
            form = self.form()
            form.email.data = current_user.email
            form.about_me.data = current_user.aboutme
        else:
            if current_user.can(Permission.ADMINISTER):
                user_info = User.query.filter_by(username=username, delete=False).first()
                if user_info:
                    form = self.admin_form()
                    form.email.data = user_info.email
                    form.about_me.data = user_info.aboutme
                    form.role.data = user_info.role.name
                else:
                    flash(u'用户不存在')
                    return redirect(url_for('main.index'))
            else:
                abort(403)
        return render_template('edit_profile.html', form=self.form(), u=current_user)

    def post(self, username):
        if not username:
            form = self.form(request.form)
            user = current_user
        else:
            if current_user.can(Permission.ADMINISTER):
                form = self.form(request.form)
                user = User.query.filter_by(username=username, delete=False).first()
                if user:
                    if not current_user.verify_password(form.oripassword.data):
                        flash(u'管理员密码输入错误')
                        return redirect(url_for('main.editprofile', username=username))
                else:
                    flash(u'用户不存在')
                    return redirect(url_for('main.index'))
            else:
                abort(403)

        self.change_profile(user, form, True if username else False)
        return redirect(url_for('main.user', username=username))

    @staticmethod
    def change_profile(user, form, admin=False):
        user.password = form.password.data
        user.email = form.email.data
        user.aboutme = form.about_me.data
        if admin:
            new_role = Role.query.filter_by(name=form.role.data)
            if new_role:
                user.role = new_role
        user.save()


class OperationLog(MethodView):
    decorators = [login_required, admin_required]

    def get(self, page):
        per_page = 10
        count = UserOperation.query.count()
        query = UserOperation.query.order_by(UserOperation.id.desc())\
                                  .paginate(page=page, per_page=per_page, error_out=False)
        foot_bar = Pagination(css_framework='bootstrap3', link_size='sm',
                              show_single_page=False, page=page, per_page=per_page,
                              total=count, format_total=True, format_number=True)
        return render_template('log.html', records=query.items,
                                page=page, per_page=per_page, pagination=foot_bar)


class Ban(MethodView):
    decorators = [login_required, admin_required]

    def __init__(self):
        self.form = BanKeywordForm

    def get(self, page):
        per_page = 10
        count = BanList.query.count()
        pagination = BanList.query.filter_by(delete=False)\
                                  .paginate(page=page, per_page=per_page, error_out=False)  # TODO: 把关键词读入配置减少查询次数
        foot_bar = Pagination(css_framework='bootstrap3', link_size='sm',
                              show_single_page=False, page=page, per_page=per_page,
                              total=count, format_total=True, format_number=True)
        template_param = {
            'keywords': pagination,
            'page': page,
            'per_page': per_page,
            'pagination': foot_bar,
            'form': self.form()
        }
        return render_template('ban.html', **template_param)

    def post(self):
        data = request.get_json()
        if data:
            keyword = data['keyword']
            result = BanList.query.filter_by(rule=keyword).first()
            if result:
                result.delete()
                flash(u'成功删除关键词')
            else:
                flash(u'该关键词不存在')
        elif request.form:
            form = self.form(request.form)
            if form.validate():
                if not BanList.query.filter_by(rule=form.keyword.data).exists():
                    ban = BanList(rule=form.keyword.data)
                    ban.save()
                    flash(u'添加关键词成功')
        return redirect(url_for('main.ban'))


@main.route('/code')
@login_required
def code():
    code = request.args.get('code')
    flag = RefreshCode(code)
    if flag is True:
        return render_template('success.html')
    else:
        return render_template('failed.html', e=flag)


@main.route('/limit')
@login_required
def limit():
    flag = current_user.is_administrator(g.user)
    if flag is True:
        form = LimitKeywordForm()
