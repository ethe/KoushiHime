# -*- coding:utf-8 -*-

import redis
from flask import current_app


class Model(object):
    client = redis.StrictRedis(**current_app.config["DATABASE_URI"])
