# -*- coding: utf-8 -*-

from models import User
from forms import LoginForm
from flask.views import MethodView
from flask.ext.login import login_user, login_required, logout_user
from flask import render_template, request, flash, redirect, url_for


class Login(MethodView):
    def __init__(self):
        self.form = LoginForm

    def get(self):
        return render_template('auth/login.html', form=self.form())

    def post(self):
        form = self.form(request.form)
        if form.validate():
            username = form.username.data
            try:
                user = User.query.filter_by(username=username).first()
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
