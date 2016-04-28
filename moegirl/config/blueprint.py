# -*- coding:utf-8 -*-

from moegirl.main import main as main_blueprint
from moegirl.auth import auth as auth_blueprint


def regist(app):
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
