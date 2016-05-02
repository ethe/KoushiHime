# -*- coding:utf-8 -*-

import os
from error import configure_errorhandlers
from . import blueprint


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'the answer of life, universe and everything'
    WTF_CSRF_ENABLED = True  # 启用csrf保护
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 在每次会话被销毁前自动commit未commit的会话
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # flask-sqlalchemy将追踪orm对象变化并发送信号

    MOEGIRL_API_ROOT = "https://zh.moegirl.org/api.php"
    CUTTING_WEIGHT_INIT = 0  # 插队权重初始化

    WEIBO_AUTH_CONFIG = {  # 微博登录验证配置
        'APP_KEY': '563928974',
        'APP_SECRET': '',
        'PUSHEDPREFIX': 'PUSHED-',
        'EDITEDPREFIX': 'EDITED-',
        'EXPIRETIME': '72*3600',
        'THREEDAYS': 259200,
        'Code': '7581b56419b5ea52abc39c0f282716e6'
    }
    WEIBO_CALLBACK_URL = os.environ.get('WEIBO_CALLBACK_URL') or 'http://gengxinji.acg.moe/code'  # 微博回调url

    @staticmethod
    def init_app(app):  #: 初始化
        configure_errorhandlers(app)
        blueprint.regist(app)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '../../data.sqlite')


config = {
    'default': DevelopmentConfig,

    'testing': TestingConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
}
