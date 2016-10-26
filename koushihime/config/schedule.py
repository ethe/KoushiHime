# -*- coding:utf-8 -*-

from celery.schedules import crontab


class CelerySchedule:
    CELERY_TIMEZONE = 'Etc/GMT-8'  # 时区设置
    CELERYBEAT_SCHEDULE = {
        'midnight_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='0-1', minute='0,30'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'early_morning_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='2-5', minute='0'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'morning_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='6-9', minute='0,30'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'afternoon_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='10-17', minute='0,0-59/15'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'late_afternoon_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='18-21', minute='0,0-59/10'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'evening_push': {
            'task': 'tasks.push',
            'schedule': crontab(hour='22-23', minute='0,0-59/15'),
            'args': (),
        },
        'check_update': {
            'task': 'tasks.check_update',
            'schedule': crontab(hour='0-23', minute='0,0-59/15'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        },
        'reset': {
            'task': 'tasks.reset',
            'schedule': crontab(hour='0', minute='5'),
            'args': (),
            'options': {
                    'expires': 5*60,
                    },
        }
    }
