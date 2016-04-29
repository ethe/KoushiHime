# -*- coding: utf-8 -*-
# from flask import render_template, redirect, request, url_for, flash
# from flask.ext.login import login_user, login_required, logout_user
# from .. model import User
# from . import auth
# from .. import r, login_manager
from flask.views import MethodView
from flask import render_template, request
from models import User
from forms import LoginForm


class Login(MethodView):
    def __init__(self):
        self.form = LoginForm

    def get(self):
        return render_template('auth/login.html', form=self.form)

    def post(self):
        form = self.form(request.form)
        if form.validate():
            username = form.username.data
            try:
                user = User.query.filter_by(username=username).first()
            except Exception, e:
                raise e


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    u = User()
    if request.method == 'POST' and form.validate():
        userlist = r.lrange('users', 0, -1)
        if form.username.data in userlist:
            if u.verify_password(form.password.data):
                login_user(load_user(form.username.data), form.remember.data)
                return redirect(request.args.get('next') or url_for('main.update'))
        flash('错误的用户名或密码')
    return render_template('auth/login.html', form=form)


# @auth.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('已登出')
#     return redirect(url_for('main.index'))


# @login_manager.user_loader
# def load_user(username):
#     u = User()
#     u.id = username
#     return u
