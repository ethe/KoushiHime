# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Email


class LoginForm(Form):
    email = StringField(u'用户名', [validators.Required(), validators.Length(min=1, max=32), Email()])
    password = PasswordField(u'密码', [validators.Required(), validators.Length(min=6, max=30)])
    remember = BooleanField(u'保持登入状态')
    submit = SubmitField(u'登入')
