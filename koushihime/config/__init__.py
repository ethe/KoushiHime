# -*- coding:utf-8 -*-

import os
from error import configure_errorhandlers
from . import blueprint
from schedule import CelerySchedule
from koushihime.utils import Env


env = Env()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(CelerySchedule):
    SECRET_KEY = env.get('SECRET_KEY') or 'the answer of life, universe and everything'
    WTF_CSRF_ENABLED = True  # 启用csrf保护
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 在每次会话被销毁前自动commit未commit的会话
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # flask-sqlalchemy将追踪orm对象变化并发送信号

    MOEGIRL_API_ROOT = "https://zh.moegirl.org/api.php"

    WEIBO_AUTH_CONFIG = {  # 微博登录验证配置
        'APP_KEY': env.get('WEIBO_APP_KEY') or '563928974',
        'APP_SECRET': env.get('WEIBO_SECRET_KEY') or '',
        'CALLBACK': env.get('WEIBO_CALLBACK') or 'http://gengxinji.acg.moe/code',
        'ACCESS_TOKEN': env.get("ACCESS_TOKEN"),
        'EXPIRE_TIME': env.get("EXPIRE_TIME") or str(72 * 3600)
    }

    @staticmethod
    def init_app(app):  #: 初始化
        configure_errorhandlers(app)
        blueprint.regist(app)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = env.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data-dev.sqlite')
    # celery中间人
    BROKER_URL = 'sqla+' + SQLALCHEMY_DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = env.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data-test.sqlite')
    BROKER_URL = 'sqla+' + SQLALCHEMY_DATABASE_URI


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data.sqlite')
    BROKER_URL = 'sqla+' + SQLALCHEMY_DATABASE_URI


config = {
    'default': DevelopmentConfig,

    'testing': TestingConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
}
