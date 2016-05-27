# -*- coding: utf-8 -*-

import urllib
from urllib2 import HTTPError
from datetime import datetime
from flask.views import MethodView
from flask.ext.login import current_user, login_required
from flask.ext.paginate import Pagination as PaginationBar
from flask import render_template, redirect, url_for, request, jsonify, flash, current_app, abort
from koushihime.auth.models import UserOperation, User, Role
from koushihime.auth.constants import Permission, Operation
from koushihime.utils import Pagination, admin_required, Env
from koushihime.utils.moegirl import MoegirlQuery, MoegirlImage
from koushihime.utils.weibo import APIClient
from . import main
from utils import recent_have_pushed, have_auto_catched
from models import WaitingQueue, BanList
from forms import PushForm, AddUserForm, EditProfileForm, AdminEditProfileForm, BanKeywordForm


@main.before_request
def before_request():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    elif current_user.is_blocked:
        return render_template('main/auth/block.html')
    else:
        current_user.last_seen = datetime.utcnow()
        current_user.save()


class Index(MethodView):

    def get(self):
        if not current_user:
            return redirect(url_for("auth.login"))
        config = current_app.config["WEIBO_AUTH_CONFIG"]
        callback = urllib.quote(config["CALLBACK"])
        app_key = config["APP_KEY"]
        return render_template('main/index.html', callback=callback, app_key=app_key)


class Update(MethodView):
    decorators = [login_required]

    def get(self, page):
        per_page = 10
        unpushed_entry = WaitingQueue.query.order_by(WaitingQueue.cutting_weight.desc()).all()
        pagination = Pagination(unpushed_entry, per_page)
        current_page = pagination.page(page)
        foot_bar = PaginationBar(css_framework='bootstrap3', link_size='sm',
                                 show_single_page=True, page=page,
                                 per_page=per_page, total=len(unpushed_entry),
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
        return render_template('main/update.html', **result)

    def post(self, page):
        data = request.get_json()
        if data['action'] == 'post':
            title = data["title"]
            env = Env()
            current_weight = env.get("CUTTING_WEIGHT_INIT")
            entry = WaitingQueue.query.filter_by(title=title).first()
            if entry:
                entry.cutting_weight = current_weight + 1  # FIXME: 即使条目处于权重最高状态亦可增加权限
                entry.save()
                env.set("CUTTING_WEIGHT_INIT", entry.cutting_weight)
        elif data['action'] == 'del':
            title = data['title']
            UserOperation(user_id=current_user.id, operation=Operation.DELETE, title=title).save()
            query = WaitingQueue.query.filter_by(title=data['title']).first()
            if query:
                query.delete()
        response = jsonify({'result': True})
        return response


class ManualUpdate(MethodView):
    decorators = [login_required]

    def __init__(self):
        self.form = PushForm

    def get(self):
        return render_template('main/mupdate.html', form=self.form(), pushtime=10)

    def post(self):
        if current_user.can(Permission.MANUAL_PUSH):
            form = self.form(request.form)
            if form.validate():
                title = form.pushtitle.data
                result = self.check_push_validate(title.encode("utf-8"))
                if result:
                    try:
                        image = MoegirlImage(title)
                    except HTTPError as e:
                        flash(u"请求萌百错误，错误码如下{}，请联系管理员".format(e))
                        return redirect(url_for('main.mupdate'))
                    if image.path:
                        entry = WaitingQueue(title=title, image=image.path)
                        env = Env()
                        current_weight = env.get("CUTTING_WEIGHT_INIT")
                        entry.cutting_weight = current_weight + 1
                        entry.save()
                        env.set("CUTTING_WEIGHT_INIT", entry.cutting_weight)
                        UserOperation(user_id=current_user.id, title=title, operation=Operation.PUSH).save()
                        if form.industry.data:
                            try:
                                from koushihime.crontab import push
                                push()
                            except:
                                pass
                            flash(u"操作成功，词条将立即推送")
                        else:
                            flash(u"操作成功，词条将在下一次推送中推送")
                    else:
                        flash(u"无法取得图片，请重试")
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
            baned_from_regex = moegirl_entry.ban_from_regex()
            has_pushed = recent_have_pushed(title.decode("utf-8"))  # TODO: 改成自动冒泡
            has_catched = have_auto_catched(title.decode("utf-8"))
            result = baned_from_moegirl is False \
                        and has_pushed is False \
                        and has_catched is False \
                        and baned_from_regex is False
            return result
        else:
            return False


class UserInfo(MethodView):
    decorators = [login_required]

    def get(self, username):
        is_admin = current_user.can(Permission.ADMINISTER)
        if current_user.username == username or is_admin is True:
            user_info = User.query.filter_by(username=username, deleted=False).first()
            if not user_info:
                abort(404)
            return render_template('main/user.html', u=user_info, username=user_info.username)
        else:
            abort(403)


class UserList(MethodView):
    decorators = [login_required, admin_required]

    def __init__(self):
        self.form = AddUserForm

    def get(self):
        userlist = User.query.filter_by(deleted=False).all()
        return render_template('main/userlist.html', userlist=userlist, form=self.form())

    def post(self):
        data = request.get_json()
        if data:
            if data['action'] == 'edit':
                username = data['username']
            else:
                username = data['username']
                try:
                    User.query.filter_by(username=username, deleted=False).first().delete()
                except:
                    flash(u'用户不存在')
            return jsonify({"status": 302, "location": url_for('main.editprofile', username=username)})
        elif request.form:
            self.add_user()
        return redirect('userlist')

    def add_user(self):
        form = self.form(request.form)
        if form.validate():
            role = Role.query.filter_by(name=form.role.data).first()
            if role:
                if not User.query.filter_by(email=form.email.data).first():
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
            form = self.form()
            form.email.data = current_user.email
            form.about_me.data = current_user.aboutme
        else:
            if current_user.can(Permission.ADMINISTER):
                user_info = User.query.filter_by(username=username, deleted=False).first()
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
        return render_template('main/edit_profile.html', form=form, u=current_user)

    def post(self, username):
        if not username:
            form = self.form(request.form)
            user = current_user
        else:
            if current_user.can(Permission.ADMINISTER):
                form = self.form(request.form)
                user = User.query.filter_by(username=username, deleted=False).first()
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
        foot_bar = PaginationBar(css_framework='bootstrap3', link_size='sm',
                                 show_single_page=False, page=page, per_page=per_page,
                                 total=count, format_total=True, format_number=True)
        return render_template('main/log.html', records=query.items,
                                page=page, per_page=per_page, pagination=foot_bar, Operation=Operation)


class KeywordBan(MethodView):
    decorators = [login_required, admin_required]

    def __init__(self):
        self.form = BanKeywordForm

    def get(self, page):
        per_page = 10
        count = BanList.query.filter_by(deleted=False).count()
        pagination = BanList.query.filter_by(deleted=False)\
                                  .paginate(page=page, per_page=per_page, error_out=False)  # TODO: 把关键词读入配置减少查询次数
        foot_bar = PaginationBar(css_framework='bootstrap3', link_size='sm',
                                 show_single_page=False, page=page, per_page=per_page,
                                 total=count, format_total=True, format_number=True)
        template_param = {
            'keywords': pagination.items,
            'page': page,
            'per_page': per_page,
            'pagination': foot_bar,
            'form': self.form()
        }
        return render_template('main/ban.html', **template_param)

    def post(self, page):
        data = request.get_json()
        if data:
            keyword = data['keyword']
            result = BanList.query.filter_by(rule=keyword).first()
            if result:
                result.delete()
                flash(u'成功删除关键词')
            else:
                flash(u'该关键词不存在')
            return jsonify({"status": 302, "location": url_for('main.ban')})
        elif request.form:
            form = self.form(request.form)
            if form.validate():
                if not BanList.query.filter_by(rule=form.keyword.data).first():
                    ban = BanList(rule=form.keyword.data)
                    ban.save()
                    flash(u'添加关键词成功')
                else:
                    flash(u'重复添加关键词')
        return redirect(url_for('main.ban'))


class WeiboAuthCallback(MethodView):
    decorators = [login_required, admin_required]

    def get(self):
        self.auth_code = request.args.get("code")
        result = self.fresh_access()
        if result is True:
            return render_template('main/success.html')
        else:
            return render_template('main/failed.html', e=result)

    def fresh_access(self):
        config = current_app.config["WEIBO_AUTH_CONFIG"]
        callback = config["CALLBACK"]
        app_key = config["APP_KEY"]
        app_secret_key = config["APP_SECRET"]
        try:
            client = APIClient(app_key=app_key, app_secret=app_secret_key, redirect_uri=callback)
            token_data = client.request_access_token(self.auth_code)
            access_token, expires_in = token_data.access_token, token_data.expires_in
        except BaseException as e:
            return e
        config["ACCESS_TOKEN"] = access_token
        config["EXPIRE_TIME"] = expires_in
        env = Env()
        env.set("ACCESS_TOKEN", access_token)
        env = Env()
        env.set("EXPIRE_TIME", expires_in)
        return True
