# -*- coding: utf-8 -*-

import os
from flask import current_app
from urllib import quote
from koushihime import db, celery, create_app
from urllib2 import HTTPError
from koushihime.main.views import ManualUpdate
from koushihime.main.models import WaitingQueue, PushRecord, RulePushCount
from koushihime.utils import Env
from koushihime.utils.moegirl import MoegirlImage, get_recent_changes
from koushihime.utils.weibo import WeiboAPI


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
with app.app_context():
    celery.conf.update(current_app.config)


@celery.task(name='tasks.check_update')
def check_update():
    try:
        change_list = get_recent_changes()
    except HTTPError as e:
        print e.code, e.msg
        raise e
    with app.app_context():
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
    with app.app_context():
        env = Env()
        entry = WaitingQueue.query.order_by(WaitingQueue.cutting_weight.desc()).first()
        if entry:
            weibo = WeiboAPI(env.get("COOKIE"))
            with open(entry.image, 'rb') as f:
                resp = weibo.post(
                    entry.title + ' ' + 'https://zh.moegirl.org/' + quote(entry.title.encode('utf-8')),
                    pic=weibo.upload_image(f)['pic_id'])
                if isinstance(resp, dict) and resp['ok'] == 1:
                    result = True
                else:
                    result = False
            db.session.delete(entry)
            record = PushRecord(title=entry.title, is_success=result)
            db.session.add(record)
            db.session.commit()
        else:
            if retry is False:
                check_update()
                return push(retry=True)
            else:
                raise Exception("Queue empty error")


@celery.task(name='tasks.reset')
def reset():
    with app.app_context():
        query = WaitingQueue.query.filter_by().all()
        if query:
            for entry in query:
                db.session.delete(entry)
            db.session.commit()
        os.system("rm -f ./koushihime/imgcache/*")
        # 权重重置
        env = Env()
        env.set("CUTTING_WEIGHT_INIT", 0)

        # 正则检测规则推送次数限制重置
        query = RulePushCount.query.filter_by().all()
        if query:
            for entry in query:
                entry.count = entry.config.time_limit
                db.session.add(entry)
            db.session.commit()
