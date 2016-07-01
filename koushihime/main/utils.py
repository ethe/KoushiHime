# -*- coding:utf-8 -*-

import datetime
from koushihime.main.models import PushRecord, WaitingQueue


def recent_have_pushed(title, hours=72):
    limit_date = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    query = PushRecord.query.filter(PushRecord.title == title, PushRecord.pushed_time > limit_date).all()
    if query:
        return True
    return False


def have_auto_catched(title):
    query = WaitingQueue.query.filter_by(title=title).all()
    if query:
        return True
    return False
