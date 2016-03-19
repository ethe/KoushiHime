# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField,TextAreaField,SelectField,validators
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
class AddUserForm(Form):
    username=StringField('用户名',[validators.Length(min=0,max=30),validators.Required()])
    password=PasswordField('密码',[validators.Length(min=6,max=30),validators.EqualTo('password2',message='两次输入不一致'),validators.Required()])
    password2=PasswordField('确认密码',[validators.Length(min=6,max=30),validators.Required()])
    email=StringField('邮件地址',[validators.Length(min=6,max=30),validators.Required()])
    role=SelectField('职务')
    submit=SubmitField('提交')
    oripassword=PasswordField('请输入管理员密码以验证身份',[validators.Required(),validators.Length(min=6,max=30)])
    def __init__(self,*args,**kwargs):
        super(AddUserForm,self).__init__(*args,**kwargs)
        self.role.choices=[('管理员','管理员'),('巡察姬','巡察姬')]
class AdminEditProfileForm(Form):
    password=PasswordField('密码',[validators.Length(min=0,max=30),validators.EqualTo('password2',message='两次输入不一致')])
    password2=PasswordField('确认密码',[validators.Length(min=0,max=30)])
    email=StringField('邮件地址',[validators.Length(min=0,max=30)])
    role=SelectField('职务')
    about_me=TextAreaField('个人签名')
    submit=SubmitField('提交')
    oripassword=PasswordField('请输入管理员密码以验证身份',[validators.Required(),validators.Length(min=6,max=30)])
    def __init__(self,*args,**kwargs):
        super(AdminEditProfileForm,self).__init__(*args,**kwargs)
        self.role.choices=[('管理员','管理员'),('巡察姬','巡察姬'),('封禁','封禁')]
class BanKeywordForm(Form):
    keyword=StringField('屏蔽关键词(请使用python正则表达式书写)',[validators.Length(min=3,max=100),validators.Required()])
    submit=SubmitField('提交')
class LimitKeywordForm(Form):
    limitcategory = StringField('限制分类(请在分类名前加Category:',[validators.Required(),validators.Length(min=8,max=100)])
    catsubmit = SubmitField('提交')
    limittopic = StringField('限制标题(请使用python正则表达式书写)',[validators.Length(min=3,max=100),validators.Required()])
    topicsubmit = SubmitField('提交')