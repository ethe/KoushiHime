# -*- coding:utf-8 -*-

from math import ceil


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
