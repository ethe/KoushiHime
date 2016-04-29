# # -*- coding: utf-8 -*-
# from flask import render_template, redirect, request, url_for, flash
# from flask.ext.login import login_user, login_required, logout_user
# from .. model import User
# from . import auth
# from .. import r, login_manager
# from .form import LoginForm
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')


# @auth.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm(request.form)
#     u = User()
#     if request.method == 'POST' and form.validate():
#         userlist = r.lrange('users', 0, -1)
#         if form.username.data in userlist:
#             if u.verify_password(form.password.data):
#                 login_user(load_user(form.username.data), form.remember.data)
#                 return redirect(request.args.get('next') or url_for('main.update'))
#         flash('错误的用户名或密码')
#     return render_template('auth/login.html', form=form)


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
