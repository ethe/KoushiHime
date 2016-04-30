# -*- coding: utf-8 -*-

from datetime import datetime
from flask.ext.login import UserMixin
from constants import Permission
from koushinn import db, login_manager
from koushinn.utils.database import CRUDMixin
from werkzeug.security import generate_password_hash, check_password_hash


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

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def init_roles():
        roles = {
            'Blocked': Permission.BLOCKED,
            'Rounder': Permission.READ | Permission.MANUEL_PUSH,
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

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    push_records = db.relationship('UserOpration', backref='handlers', lazy='dynamic')
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


class UserOpration(db.Model, CRUDMixin):
    __tablename__ = 'user_oprations'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    opration = db.Column(db.SmallInteger())
    title = db.Column(db.Text())
    created_time = db.Column(db.DateTime(), default=datetime.utcnow)
