# -*- coding: utf-8 -*-

from utils import make_celery
from flask import current_app
from koushihime.main.views import ManualUpdate
from koushihime.main.models import WaitingList
from koushihime.utils.moegirl import MoegirlImage, get_recent_changes


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
                    entry = WaitingList(title=title, image=image.path)
                    entry.save()
