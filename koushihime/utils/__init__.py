# -*- coding:utf-8 -*-

import functools
from math import ceil
from koushihime import db
from flask import abort
from flask.ext.login import current_user
from koushihime.auth.constants import Permission


def admin_required():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if not current_user.can(Permission.ADMINISTER):
                abort(403)
            return func(*args, **kw)
        return wrapper
    return decorator


class CRUDMixin(object):
    def __repr__(self):
        return "<class: {0}, id: {1}>".format(self.__class__.__name__, self.id)

    def save(self):
        """Saves the object to the database."""
        db.session.add(self)
        try:
            db.session.commit()
            return self
        except Exception, e:
            db.session.rollback()
            raise e

    def delete(self, sign='delete'):
        """Delete the object from the database."""
        if hasattr(self, sign):
            self.sign = True
            db.session.add(self)
        else:
            db.session.delete(self)
        try:
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            raise e


class Pagination(object):

    def __init__(self, total, per_page):
        self.total = total
        self.per_page = per_page
        self.total_count = len(total)

    @property
    def pages_num(self):
        return int(ceil(self.total_count / float(self.per_page)))

    def page(self, page):
        if page >= 1:
            start = page * self.per_page - self.per_page
            end = page * self.per_page
            return self.total[start:end if end < self.total_count else self.total_count]
        else:
            return []


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
