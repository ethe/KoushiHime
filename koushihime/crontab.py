# -*- coding: utf-8 -*-

import os
import json
from koushihime import db, celery, create_app
from urllib import quote
from urllib2 import Request, urlopen
from flask import current_app
from koushihime.main.views import ManualUpdate
from koushihime.main.models import WaitingQueue, PushRecord
from koushihime.utils import _decode_dict, Env
from koushihime.utils.moegirl import MoegirlImage, get_recent_changes
from koushihime.utils.weibo import APIClient


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()


@celery.task(name='tasks.check_update')
def check_update():
    change_list = get_recent_changes()
    for i in change_list:
        if i['newlen'] >= 1000:
            title = i['title']
            result = ManualUpdate.check_push_validate(title)
            if result:
                image = MoegirlImage(title)
                if image.path:
                    entry = WaitingQueue(title=title.decode("utf-8"), image=image.path)
                    entry.save()
                    break


@celery.task(name='tasks.push')
def push(retry=False):
    env = Env()
    config = current_app.config["WEIBO_AUTH_CONFIG"]
    entry = WaitingQueue.query.order_by(WaitingQueue.cutting_weight.desc()).first()
    if entry:
        weibo_client = APIClient(app_key=config["APP_KEY"], app_secret=config["APP_SECRET"], redirect_uri=config["CALLBACK"])
        weibo_client.set_access_token(env.get("ACCESS_TOKEN"), env.get("EXPIRE_TIME"))
        short_url = get_short_url(entry.title)
        with open(entry.image, 'rb') as f:
            try:
                weibo_client.statuses.upload.post(status=entry.title + short_url, pic=f)
                result = True
            except:
                result = False
        db.session.delete(entry)
        record = PushRecord(title=entry.title, is_success=result)
        db.session.add(record)
        db.session.commit()
    else:
        if retry is False:
            check_update()
            push(retry=True)
        else:
            raise "Queue empty error"


@celery.task(name='tasks.reset')
def reset():
    query = WaitingQueue.query.filter_by().all()
    if query:
        for entry in query:
            db.session.delete(entry)
        db.commit()
    os.system("rm -f ./koushihime/imgcache/*")
    # 权重重置
    env = Env()
    env.set("CUTTING_WEIGHT_INIT", 0)


def get_short_url(title):
    env = Env()
    request_url = 'https://api.weibo.com/2/short_url/shorten.json?access_token=' + \
        env.get('ACCESS_TOKEN') + '&url_long=http://zh.moegirl.org/' + quote(title.encode('utf-8'))
    req = Request(request_url)
    res = urlopen(req).read()
    data = json.loads(res, object_hook=_decode_dict)
    short_url = data['urls'][0]['url_short']
    return short_url
