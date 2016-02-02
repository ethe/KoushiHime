from flask.ext.wtf import Form
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from wtforms import StringField
class PushForm(Form):
    title=StringField('词条名',[validators.Required(),validators.Length(min=1,max=256)])
    submit=SubmitField('推送')