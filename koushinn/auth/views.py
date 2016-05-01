# -*- coding: utf-8 -*-

from datetime import datetime
from . import auth
from models import User
from forms import LoginForm
from flask.views import MethodView
from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_user, login_required, logout_user, current_user


@auth.before_app_request
@login_required
def before_request():
    if current_user.is_blocked():
        return render_template('auth/block.html')
    else:
        current_user.last_seen = datetime.utcnow()
        current_user.save()


class Login(MethodView):
    def __init__(self):
        self.form = LoginForm

    def get(self):
        return render_template('auth/login.html', form=self.form())

    def post(self):
        form = self.form(request.form)
        if form.validate():
            email = form.email.data
            try:
                user = User.query.filter_by(email=email).first()
            except Exception, e:
                flash(u"程序内部错误，看见此条信息请尝试刷新或联系管理员")
                raise e
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            flash(u"用户名或密码不正确")
        return render_template('auth/login.html', form=form)


class Logout(MethodView):
    decorators = [login_required]

    def get():
        logout_user()
        flash(u"已登出")
        return redirect(url_for('main.index'))
