# -*- coding: utf-8 -*-

from datetime import datetime
from flask.ext.login import UserMixin
from moegirl import db, login_manager
from moegirl.utils.database import CRUDMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Permission:
    """
    使用位运算标记用户权限
    每一位表示一种权限
    """
    BLOCKED = 0x00
    READ = 0x01
    ADMINISTER = 0x80


@login_manager.user_loader
def load_user(user_id):
    """
    flask-login 要求完成的方法
    """
    return User.query.get(int(user_id))


class Role(db.Model, CRUDMixin):
    """
    权限组
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def init_roles():
        roles = {
            'Blocked': Permission.BLOCKED,
            'Rounder': Permission.READ,
            'Administrator': 0xff
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r]
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model, CRUDMixin):
    """
    用户
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    push_records = db.relationship('PushRecord', backref='oprate_user', lazy='dynamic')
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change_password(self, new_password):
        self.password = new_password
        db.session.add(self)
        return True

    def change_profile(self, new_email=None, new_aboutme=None):
        if new_email:
            self.email = new_email
        if new_aboutme:
            self.about_me = new_aboutme
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_blocked(self):
        return self.role.permissions == Permission.BLOCKED


class PushRecord(db.Model, CRUDMixin):
    """
    用户的手动操作记录
    """
    __tablename__ = 'push_records'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.Text())
    date = db.Column(db.DateTime(), default=datetime.utcnow)
