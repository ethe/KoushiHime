# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField, SelectField, IntegerField, validators


class PushForm(Form):
    pushtitle = StringField(u'条目名', [validators.Required(), validators.Length(min=1, max=60)])
    submit = SubmitField(u'推送')
    industry = BooleanField(u'立即推送')


class EditProfileForm(Form):
    password = PasswordField(
        u'新密码', [validators.Length(min=0, max=30), validators.EqualTo(u'password2', message=u'两次输入不一致')])
    password2 = PasswordField(u'确认密码', [validators.Length(min=0, max=30)])
    email = StringField(u'邮件地址', [validators.Length(min=0, max=30)])
    about_me = TextAreaField(u'个人签名')
    oripassword = PasswordField(u'请输入原密码以验证身份', [validators.Required(), validators.Length(min=6, max=30)])
    submit = SubmitField(u'提交')


class AddUserForm(Form):
    username = StringField(u'用户名', [validators.Length(min=0, max=30), validators.Required()])
    password = PasswordField(u'密码', [validators.Length(min=6, max=30),
                             validators.EqualTo(u'password2', message=u'两次输入不一致'), validators.Required()])
    password2 = PasswordField(u'确认密码', [validators.Length(min=6, max=30), validators.Required()])
    email = StringField(u'邮件地址', [validators.Length(min=6, max=30), validators.Required()])
    role = SelectField(u'职务')
    submit = SubmitField(u'提交')
    oripassword = PasswordField(u'请输入管理员密码以验证身份', [validators.Required(), validators.Length(min=6, max=30)])

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [('Administrator', u'管理员'), ('Watchman', u'巡察姬')]


class AdminEditProfileForm(Form):
    password = PasswordField(
        u'密码', [validators.Length(min=0, max=30), validators.EqualTo(u'password2', message=u'两次输入不一致')])
    password2 = PasswordField(u'确认密码', [validators.Length(min=0, max=30)])
    email = StringField(u'邮件地址', [validators.Length(min=0, max=30)])
    role = SelectField(u'职务')
    about_me = TextAreaField(u'个人签名')
    submit = SubmitField(u'提交')
    oripassword = PasswordField(u'请输入管理员密码以验证身份', [validators.Required(), validators.Length(min=6, max=30)])

    def __init__(self, *args, **kwargs):
        super(AdminEditProfileForm, self).__init__(*args, **kwargs)
        self.role.choices = [('Administrator', u'管理员'), ('Watchman', u'巡察姬'), ('Blocked', u'封禁')]


class BanKeywordForm(Form):
    keyword = StringField(u'屏蔽关键词(请使用python正则表达式书写)', [validators.Length(min=0, max=100), validators.Required()])
    time_limit = IntegerField(u'一天内限制推送次数，缺省为0即永远不推送', default=0)
    submit = SubmitField(u'提交')


class LimitKeywordForm(Form):
    limitcategory = StringField(u'限制分类(请在分类名前加Category:', [validators.Required(), validators.Length(min=8, max=100)])
    catsubmit = SubmitField(u'提交')
    limittopic = StringField(u'限制标题(请使用python正则表达式书写)', [validators.Length(min=3, max=100), validators.Required()])
    topicsubmit = SubmitField(u'提交')
