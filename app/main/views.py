from datetime import datetime
from flask import render_template,session,redirect,url_for,request,abort
from flask.ext.login import login_required
from .. model import Page
from datetime import datetime
import pdb
from . import main
@main.route('/')
def index():
    return render_template('base.html')
@main.route('/update',methods=['GET','POST'])
@login_required
def update():
    p=Page()
    title=[]
    title=p.GetTitles()
    pdb.settrace()
    if request.method == 'POST':
        jsondata=request.get_json()
        print jsondata
        title=jsondata['title']
        flag=p.Break(title)
        if flag==True:
            pass
        else: 
            abort(403)
    return render_template('update.html',title=title,current_time=datetime.utcnow())
