# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template,session,redirect,url_for,request,abort,flash
from flask.ext.login import login_required
from MU_utils import GetNamespace
from .. model import Page
from datetime import datetime
import pdb
from .form import PushForm
from . import main
from MU_update import ForbiddenItemsFilter,ForbiddenItemPushed,ForbiddenItemGet
from MU_utils import GetNamespace
import sys
reload(sys)
sys.setdefaultencoding('utf8')
@main.route('/')
def index():
    return render_template('base.html')
@main.route('/update',methods=['GET','POST'])
@login_required
def update():
    p=Page()
    title=[]
    title=p.GetTitles()
    jsondata=request.get_json()
    if request.method == 'POST' and jsondata['action'] == 'post':
        title=jsondata['title']
        flag=p.Break(title)
        if flag==True:
            pass
        else: 
            abort(403)
    if request.method == 'POST' and jsondata['action'] == 'del':
        title=jsondata['title']
        flag=p.Delete(title)
        if flag==True:
            pass
        else:
            abort(403)
    return render_template('update.html',title=title,current_time=datetime.utcnow())
@main.route('/mupdate',methods=['GET','POST'])
@login_required
def mupdate():
    p=Page()
    form=PushForm(request.form)
    if request.method == 'POST' and form.validate():
        title=form.pushtitle.data
        ns=GetNamespace(title)
        if ns is 0:
            forbiddenflag=ForbiddenItemsFilter(title)
            pushedflag=ForbiddenItemPushed(title)
            getflag=ForbiddenItemGet(title)
            if forbiddenflag is True and pushedflag is True and getflag is True:
                flag=p.Add(title)
                if flag is True:
                    flash('推送成功，本条目将在下一次推送时被推送')
                else:
                    flash('错误-条目图片不符合要求')
            else:
                flash('错误-条目被屏蔽推送或已被更新姬自动获取')
        else:
            flash('错误-条目不在主名字空间')
    return render_template('mupdate.html',form=form)