# -*- coding: utf-8 -*-
from . import r
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from main.MU_update import GetImage
from main.MU_conf import MU_MainConfig
from collections import OrderedDict
from datetime import *
import time
import os


class User(UserMixin, object):
    def AddUser(self, username, password, role, email):
        self.password = password
        r.lpush('users', username)
        r.hset('pwd', username, self.password_hash)
        r.hset('role', username, role)
        r.hset('email', username, email)
        r.hset('aboutme', username, '')
        if role == '管理员':
            r.hset('pushtime', username, 10)
            r.hset('deltime', username, 9999)
        else:
            r.hset('pushtime', username, 1)
            r.hset('deltime', username, 1)

    def RemUser(self, username):
        r.lrem('users', username)
        r.hdel('pwd', username)
        r.hdel('role', username)
        r.hdel('email', username)
        r.hdel('pushtime', username)
        r.hdel('delname', username)
        r.hdel('aboutme', username)

    def ChangePassword(self, username, password):
        self.password = password
        r.hset('pwd', username, self.password_hash)

    def ChangeProfile(self, username, email, aboutme):
        r.hset('email', username, email)
        r.hset('aboutme', username, aboutme)

    def AdminChangeProfile(self, username, email, role, aboutme):
        r.hset('email', username, email)
        r.hset('aboutme', username, aboutme)
        r.hset('role', username, role)

    def GetPushtime(self, username):
        pushtime = r.hget('pushtime', username)
        return pushtime

    def GetDeltime(self, username):
        deltime = r.hget('deltime', username)
        return deltime

    def ChangeRole(self, username, role):
        r.hset('role', username, role)
        return username

    def CheckRole(self, username):
        userrole = r.hget('role', username)
        return userrole

    def CheckUser(self, username):
        userlist = r.lrange('users', 0, -1)
        if username in userlist:
            return True
        else:
            return False

    def GetUserList(self):
        userlist = r.lrange('users', 0, -1)
        return userlist

    def GetUserInfo(self, username):
        email = r.hget('email', username)
        role = r.hget('role', username)
        aboutme = r.hget('aboutme', username)
        setattr(self, 'email', email)
        setattr(self, 'role', role)
        setattr(self, 'aboutme', aboutme)

    def is_administrator(self, username):
        role = r.hget('role', username)
        if role == '管理员':
            return True
        else:
            return False

    def is_blocked(self, username):
        role = r.hget('role', username)
        if role == '封禁':
            return True
        else:
            return False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def GetPassword(self, username):
        self.password_hash = r.hget('pwd', username)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Page(object):
    def GetTitles(self):
        pushinglist = r.zrange('queuenumber', 0, -1)
        return pushinglist

    def Break(self, title):
        score = r.zscore('queuenumber', title)
        scorequeue = r.zrange('queuenumber', 0, int(score) - 1)
        r.zadd('queuenumber', title, 0)
        pushtime = r.hget('pushtime', g.user)
        r.hset('pushtime', g.user, int(pushtime) - 1)
        for i in range(len(scorequeue)):
            score = r.zscore('queuenumber', scorequeue[i])
            r.zadd('queuenumber', scorequeue[i], score + 1)
        return True

    def Delete(self, title):
        r.zrem('expire', MU_MainConfig.EDITEDPREFIX + title)
        r.hdel('queue', MU_MainConfig.EDITEDPREFIX + title)
        name = r.hget('img', MU_MainConfig.EDITEDPREFIX + title)
        os.remove('../imgcache/' + name)
        r.hdel('img', MU_MainConfig.EDITEDPREFIX + title)
        r.hdel('imgkey', title)
        score = r.zscore('queuenumber', title)
        r.zrem('queuenumber', title)
        scorequeue = r.zrange('queuenumber', int(score) - 1, -1)
        deltime = r.hget('deltime', g.user)
        r.hset('deltime', g.user, int(deltime) - 1)
        for i in range(len(scorequeue)):
            score = r.zscore('queuenumber', scorequeue[i])
            r.zadd('queuenumber', scorequeue[i], score - 1)
        return True

    def Add(self, title):
        flag = GetImage(title.encode('utf8'))
        if flag == True:
            timenow = time.time()
            r.zadd('expire', MU_MainConfig.EDITEDPREFIX + title, timenow)
            r.hset('queue', MU_MainConfig.EDITEDPREFIX + title, title)
            r.zadd('queuenumber', title, 0)
            scorequeue = r.zrange('queuenumber', 0, -1)
            pushtime = r.hget('pushtime', g.user)
            r.hset('pushtime', g.user, int(pushtime) - 1)
            for i in range(len(scorequeue)):
                score = r.zscore('queuenumber', scorequeue[i])
                r.zadd('queuenumber', scorequeue[i], score + 1)
            img = r.hget('img', MU_MainConfig.EDITEDPREFIX + title)
            r.hset('imgkey', title, img)
            return True
        else:
            return False

    def AddBan(self, keyword):
        r.hset('bannedkeyword', keyword, keyword)

    def GetBan(self):
        banlist = r.hkeys('bannedkeyword')
        return banlist

    def DelBan(self, keyword):
        r.hdel('bannedkeyword', keyword)

    def AddLimitCat(self, cat):
        r.hset('forbiddencategotries', cat, cat)

    def GetLimitCat(self):
        catlist = r.hkeys('forbiddencategotries')
        return catlist

    def DelLimitCat(self, cat):
        r.hdel('forbiddencategotries', cat)

    def AddLimitTopic(self, topic):
        r.hset('forbiddentopics', topic, topic)

    def GetLimitTopic(self):
        topiclist = r.hkeys('forbiddentopics')

    def DelLimitTopic(self, topic):
        r.hdel('forbiddentopics', topic)

    def RecordUpdate(self, title, username, action):
        timenow = time.time()
        utctime = datetime.utcnow()
        format = "%Y年%m月%d日%H时%M分%S秒"
        localtime = (utctime + timedelta(hours=8)).strftime(format)
        r.hset('operateuser', title, username)
        r.hset('operatetime', title, localtime)
        r.hset('operateaction', title, action)
        r.zadd('listtime', title, timenow)

    def GetRecord(self):
        keys = r.zrevrange('listtime', 0, -1)
        records = {}
        records = OrderedDict(records)
        for i in range(len(keys)):
            if i < 20:
                operateuser = r.hget('operateuser', keys[i])
                operatetime = r.hget('operatetime', keys[i])
                operateaction = r.hget('operateaction', keys[i])
                records[keys[i]] = [operateuser, operatetime, operateaction]
            else:
                break
        return records
