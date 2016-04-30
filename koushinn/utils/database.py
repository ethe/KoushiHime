# -*- coding:utf-8 -*-

from moegirl import db


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
            self.deleted = True
            db.session.add(self)
        else:
            db.session.delete(self)
        try:
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            raise e
