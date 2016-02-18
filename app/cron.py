# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
from main.MU_update import MU_UpdateData,PrepareLogin
from main.MU_utils import r
import sys
reload(sys)
sys.setdefaultencoding('utf8')
scheduler = BackgroundScheduler(daemonic=False)  
def push():
    update=MU_UpdateData()
    PrepareLogin()
    update.PostItem()
def check_update():
    update=MU_UpdateData()
    update.SaveRecentChanges()
    update.GetItemToSend()
def resetpushanddeltime():
    users=r.lrange('users',0,-1)
    for username in users:
        role=r.hget('role',username)
        if role is '管理员':
            r.hset('pushtime',username,10)
            r.hset('deltime',username,9999)
        else:
            r.hset('pushtime',username,1)
            r.hset('deltime',username,5)

scheduler.add_job(push,'cron',id='midnight_push',hour='0-1',minute='0,30')
scheduler.add_job(push,'cron',id='early_morning_push',hour='2-5',minute='0')
scheduler.add_job(push,'cron',id='morning_push',hour='6-9',minute='0,30')
scheduler.add_job(push,'cron',id='afternoon_push',hour='10-17',minute='0,15,30,45')
scheduler.add_job(push,'cron',id='late_afternoon_push',hour='18-21',minute='0,10,20,30,40,50')
scheduler.add_job(push,'cron',id='evening_push',hour='22-23',minute='0,15,30,45')
scheduler.add_job(check_update,'cron',id='check_update',hour='0-23',minute='15,35,55')
scheduler.add_job(resetpushanddeltime,'cron',id='reset',hour='0',minute='5')
def start():
    update=MU_UpdateData()
    update.SaveRecentChanges()
    update.GetItemToSend()
    scheduler.start()
