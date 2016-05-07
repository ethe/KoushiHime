# -*- coding:utf-8 -*-

from celery.schedules import crontab


class CelerySchedule:
    CELERYBEAT_SCHEDULE = {
        'midnight_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='0-1', minute='0, 30'),
            'args': (),
        },
        'early_morning_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='2-5', minute='0'),
            'args': (),
        },
        'morning_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='6-9', minute='0, 30'),
            'args': (),
        },
        'afternoon_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='10-17', minute='/15'),
            'args': (),
        },
        'late_afternoon_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='18-21', minute='/10'),
            'args': (),
        },
        'evening_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='22-23', minute='/15'),
            'args': (),
        },
        'check_update': {
            'task': 'tasks.push',
            'schedule': crontab(hour='0-23', minute='35,55'),
            'args': (),
        },
        'reset': {
            'task': 'tasks.push',
            'schedule': crontab(hour='0', minute='5'),
            'args': (),
        }
    }
