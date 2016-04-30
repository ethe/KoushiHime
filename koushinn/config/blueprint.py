# -*- coding:utf-8 -*-
"""
注册蓝图
"""

# from koushinn.main import main as main_blueprint
from koushinn.auth import auth as auth_blueprint


def regist(app):
    # app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
