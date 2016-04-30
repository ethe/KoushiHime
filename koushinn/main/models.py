# -*- coding: utf-8 -*-

from datetime import datetime
from moegirl import db
from moegirl.utils.database import CRUDMixin


class Entry(db.Model, CRUDMixin):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_auto = db.Column(db.Boolean(), default=True)
    is_pushed = db.Column(db.Boolean(), default=False)
    created_time = db.Column(db.DateTime(), default=datetime.utcnow)
    pushed_time = db.Column(db.DateTime(), nullable=True, default=None)
    ban = db.Column(db.Boolean(), default=False)
    delete = db.Column(db.Boolean(), default=False)
