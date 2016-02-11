# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField,TextAreaField,validators
import sys
reload(sys)
sys.setdefaultencoding('utf8')
class PushForm(Form):
    pushtitle=StringField('条目名',[validators.Required(),validators.Length(min=1,max=60)])
    submit=SubmitField('推送')
class EditProfileForm(Form):
    password=PasswordField('新密码',[validators.Length(min=0,max=30),validators.EqualTo('password2',message='两次输入不一致')])
    password2=PasswordField('确认密码',[validators.Length(min=0,max=30)])
    email=StringField('邮件地址',[validators.Length(min=0,max=30)])
    about_me=TextAreaField('个人签名')
    oripassword=PasswordField('请输入原密码以验证身份',[validators.Required(),validators.Length(min=6,max=30)])
    submit=SubmitField('提交')
