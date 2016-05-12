# -*- coding: utf-8 -*-

from datetime import datetime
from flask.ext.login import UserMixin
from constants import Permission
from koushihime import db, login_manager
from koushihime.utils import CRUDMixin
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
            'Watchman': Permission.READ | Permission.MANUAL_PUSH,
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
    email = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    push_records = db.relationship('UserOperation', backref='handlers', lazy='dynamic')
    password_hash = db.Column(db.String(128))
    aboutme = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean(), default=False)

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
            self.aboutme = new_aboutme
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    @property
    def is_blocked(self):
        return self.role.permissions == Permission.BLOCKED

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)


class UserOperation(db.Model, CRUDMixin):
    __tablename__ = 'user_operations'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    operation = db.Column(db.SmallInteger())
    title = db.Column(db.Text())
    created_time = db.Column(db.DateTime(), default=datetime.utcnow)
