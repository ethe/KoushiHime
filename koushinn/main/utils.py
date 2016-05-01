# -*- coding:utf-8 -*-

import datetime
from koushinn.main.models import PushRecord, WaitingList


def recent_have_pushed(title, hours=24):
    limit_date = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    query = PushRecord.query.filter(PushRecord.title == title, PushRecord.pushed_time > limit_date)
    if query:
        return True
    return False


def have_auto_catched(title):
    query = WaitingList.query.filter_by(title=title)
    if query.exists():
        return True
    return False
