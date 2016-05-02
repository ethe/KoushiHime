# -*- coding: utf-8 -*-

from utils import make_celery
from flask import current_app


celery = make_celery(current_app)
