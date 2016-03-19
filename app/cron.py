# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import logging
logging.basicConfig()
from main.MU_update import MU_UpdateData,PrepareLogin
from main.MU_utils import r
import socket
import sys
reload(sys)
sys.setdefaultencoding('utf8')
jobstores={'redis':RedisJobStore()}
excutors={'default':ThreadPoolExecutor(20),'processpool':ProcessPoolExecutor(5)}
job_defaults={'coalesce':False,'max_instances':3}
scheduler = BackgroundScheduler(jobstores=jobstores,excutors=excutors,job_defaults=job_defaults,daemonic=False)  
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
#scheduler.add_jobstore('redis',jobs_key='update.jobs',run_times_key='update.run_times')
scheduler.add_job(push,'cron',id='midnight_push',hour='0-1',minute='0,30')
scheduler.add_job(push,'cron',id='early_morning_push',hour='2-5',minute='0')
scheduler.add_job(push,'cron',id='morning_push',hour='6-9',minute='0,30')
scheduler.add_job(push,'cron',id='afternoon_push',hour='10-17',minute='0,15,30,45')
scheduler.add_job(push,'cron',id='late_afternoon_push',hour='18-21',minute='0,10,20,30,40,50')
scheduler.add_job(push,'cron',id='evening_push',hour='22-23',minute='0,15,30,45')
scheduler.add_job(check_update,'cron',id='check_update',hour='0-23',minute='35,55')
scheduler.add_job(resetpushanddeltime,'cron',id='reset',hour='0',minute='5')
#update=MU_UpdateData()
#update.SaveRecentChanges()
#update.GetItemToSend()
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    print "!!!scheduler already started, DO NOTHING"
else:
    scheduler.start()
