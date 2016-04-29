# -*- coding:utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.login import LoginManager


db = SQLAlchemy()
csrf = CsrfProtect()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
login_manager = LoginManager()


def create_app(config_name):
    """
    工厂函数，在服务运行前加载配置
    """
    app = Flask(__name__)
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    return app
