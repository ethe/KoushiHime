# -*- coding: utf-8 -*-

from datetime import datetime
from flask.ext.login import UserMixin
from moegirl import db, login_manager
from moegirl.config.database import Model
from werkzeug.security import generate_password_hash, check_password_hash


class Permission:
    READ = 0x01
    ADMINISTER = 0x80


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)


class User(UserMixin, Model):
    def regist(self, username, password, role, email):
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
