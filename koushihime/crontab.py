# -*- coding: utf-8 -*-

import os
import json
from koushihime import db
from urllib import quote
from urllib2 import Request, urlopen
from utils import make_celery
from flask import current_app
from koushihime.main.views import ManualUpdate
from koushihime.main.models import WaitingList, PushRecord
from koushihime.utils import _decode_dict
from koushihime.utils.moegirl import MoegirlImage, get_recent_changes
from koushihime.utils.weibo import APIClient


celery = make_celery(current_app)


@celery.task()
def check_update():
    change_list = get_recent_changes()
    for i in change_list:
        if i['newlen'] >= 1000:
            title = i['title']
            result = ManualUpdate.check_push_validate(title)
            if result:
                image = MoegirlImage(title)
                if image.path:
                    entry = WaitingList(title=title.decode("utf-8"), image=image.path)
                    entry.save()
                    break


@celery.task()
def push():
    config = current_app.config
    entry = WaitingList.query.order_by(WaitingList.cutting_weight.desc()).first()
    if entry:
        weibo_client = APIClient(app_key=config["APP_KEY"], app_secret=config["APP_SECRET"], redirect_uri=config["CALLBACK_URL"])
        weibo_client.set_access_token(config["ACCESS_TOKEN"], config["EXPIRE_TIME"])
        short_url = get_short_url(entry.title)
        with open("{}/{}".format("./koushihime/imgcache", entry.image), 'rb') as f:
            try:
                weibo_client.statuses.upload.post(status=entry.title + short_url, pic=f)
                result = True
            except:
                result = False
        db.session.delete(entry)
        record = PushRecord(title=entry.title, is_success=result)
        db.session.add(record)
        db.commit()


@celery.task()
def reset():
    query = WaitingList.query.filter_by()
    db.session.delete(query)
    db.commit()
    os.system("rm -f ./koushihime/imgcache/*")


def get_short_url(title):
    config = current_app.config
    request_url = 'https://api.weibo.com/2/short_url/shorten.json?access_token=' + \
        config.get('ACCESS_TOKEN') + '&url_long=http://zh.moegirl.org/' + quote(title)
    req = Request(request_url)
    res = urlopen(req).read()
    data = json.loads(res, object_hook=_decode_dict)
    short_url = data['urls'][0]['url_short']
    return short_url
