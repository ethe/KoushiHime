# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from wtforms import StringField,SubmitField,validators
class PushForm(Form):
    pushtitle=StringField('条目名',[validators.Required(),validators.Length(min=1,max=60)])
    submit=SubmitField('推送')