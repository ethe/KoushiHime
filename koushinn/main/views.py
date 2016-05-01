# -*- coding: utf-8 -*-

from datetime import datetime
from models import WaitingList
from form import PushForm
from utils import recent_have_pushed, have_auto_catched
from koushinn.utils import Pagination
from koushinn.utils.moegirl import MoegirlQuery
from flask.views import MethodView
from flask.ext.login import current_user
from koushinn.auth.models import UserOpration, User
from koushinn.auth.constants import Permission, Opration
from flask.ext.paginate import Pagination as PaginationBar
from flask import render_template, login_required, redirect, url_for, request, jsonify, flash, current_app, abort


class Index(MethodView):

    def get(self):
        if not current_user:
            redirect(url_for("auth.login"))
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

    def post(self):
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
            UserOpration(user_id=current_user.id, opration=Opration.DELETE, title=title).save()
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
                moegirl_entry = MoegirlQuery(title)
                namespace = moegirl_entry.get_namespace()
                if namespace is 0:
                    has_been_baned = moegirl_entry.banned_moegirl_category(title)
                    has_pushed = recent_have_pushed(title)  # TODO: 改成自动冒泡
                    has_catched = have_auto_catched(title)
                    # TODO: 推送检查是否被正则ban掉
                    if has_been_baned is True and has_pushed is False and has_catched is False:
                        WaitingList(title=title).save()
                        UserOpration(user_id=current_user.id, title=title).save()
                        flash(u"操作成功，词条将在下一次推送中推送")
                    else:
                        flash(u"推送条目被ban，或者已经在24小时之内推送过，或者已经被更新姬捕捉进精灵求")
                else:
                    flash(u"错误-条目不在主名字空间")
            else:
                flash(u"条目格式有问题，请检查并重新添些")
        else:
            flash(u"你没有权限")
            return redirect(url_for('main.mupdate'))


class UserInfo(MethodView):
    decorators = [login_required]

    def get(self, user_id):
        is_admin = current_user.can(Permission.ADMINISTER)
        if current_user.id == user_id or is_admin is True:
            user_info = User.query.get(int(user_id))
            if not user_info:
                abort(404)
            return render_template('user.html', u=user_info, username=user_info.username)
        else:
            abort(403)


@main.route('/userlist', methods=['GET', 'POST'])
@login_required
def userlist():
    u = User()
    form = AddUserForm()
    flag = current_user.is_administrator(g.user)
    if flag is True:
        userlist = u.GetUserList()
        jsondata = request.get_json()
        if request.method == 'POST' and jsondata:
            if jsondata['action'] == u'edit':
                username = jsondata['username']
                location = url_for('.admin_edit_profile', username=username)
                return jsonify({"status": 302, "location": location})
            else:
                username = jsondata['username']
                u.RemUser(username)
                return redirect('userlist')
        elif request.method == 'POST' and form.validate():
            pwd = u.GetPassword(g.user)
            if u.verify_password(form.oripassword.data):
                u.AddUser(form.username.data, form.password.data, form.role.data, form.email.data)
                return redirect('userlist')
        else:
            return render_template('userlist.html', userlist=userlist, form=form)
    else:
        abort(403)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    u = User()
    if request.method == 'POST' and form.validate():
        pwd = u.GetPassword(g.user)
        if u.verify_password(form.oripassword.data):
            email = form.email.data
            aboutme = form.about_me.data
            if form.password.data is not u'':
                u.ChangePassword(g.user, form.password.data)
            u.ChangeProfile(g.user, email, aboutme)
            flash('成功更新资料')
            return redirect(url_for('.user', username=g.user))
        else:
            flash('原密码输入错误！')
    u.GetUserInfo(g.user)
    form.email.data = u.email
    form.about_me.data = u.aboutme
    return render_template('edit_profile.html', form=form, u=u)


@main.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def admin_edit_profile(username):
    u = User()
    form = AdminEditProfileForm()
    flag = current_user.is_administrator(g.user)
    if request.method == 'POST' and form.validate():
        if flag is True:
            pwd = u.GetPassword(g.user)
            if u.verify_password(form.oripassword.data):
                email = form.email.data
                aboutme = form.about_me.data
                role = form.role.data
                if form.password.data is not u'':
                    u.ChangePassword(username, form.password.data)
                u.AdminChangeProfile(username, email, role, aboutme)
                flash('成功更新资料')
                return redirect(url_for('.user', username=username))
            else:
                flash('管理员密码输入错误！')
        else:
            abort(403)
    u.GetUserInfo(username)
    form.email.data = u.email
    form.about_me.data = u.aboutme
    form.role.data = u.role
    return render_template('admin_edit_profile.html', form=form, u=u)


@main.route('/log')
@login_required
def log():
    flag = current_user.is_administrator(g.user)
    if flag is True:
        p = Page()
        record = p.GetRecord()
        records = {}
        records = OrderedDict()
        total = len(record)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        keys = record.keys()
        offset = (page - 1) * per_page
        for i in range(len(keys)):
            if i < per_page and (offset + i) < len(keys):
                records[keys[offset + i]] = record[keys[offset + i]]
            else:
                break
        pagination = Pagination(css_framework='bootstrap3', link_size='sm', show_single_page=False,
                                page=page, per_page=per_page, total=total, format_total=True, format_number=True)
        return render_template('log.html', records=records, page=page, per_page=per_page, pagination=pagination)
    else:
        abort(403)


@main.route('/ban', methods=['GET', 'POST'])
@login_required
def ban():
    flag = current_user.is_administrator(g.user)
    if flag is True:
        form = BanKeywordForm()
        p = Page()
        jsondata = request.get_json()
        if request.method == 'POST':
            if jsondata:
                keyword = jsondata['keyword']
                p.DelBan(keyword)
                flash('成功删除关键词')
                location = url_for('.ban')
                return jsonify({"status": 302, "location": location})
            if form.validate():
                keyword = form.keyword.data
                p.AddBan(keyword)
                flash('成功添加关键词')
                return redirect('ban')
        banlist = p.GetBan()
        keywords = []
        total = len(banlist)
        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page
        for i in range(len(banlist)):
            if i < per_page and (offset + i) < len(banlist):
                keywords.append(banlist[offset + i])
            else:
                break
        pagination = Pagination(css_framework='bootstrap3', link_size='sm', show_single_page=False,
                                page=page, per_page=per_page, total=total, format_total=True, format_number=True)
        return render_template('ban.html', keywords=keywords, page=page, per_page=per_page, pagination=pagination, form=form)
    else:
        abort(403)


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
