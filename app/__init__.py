from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()
import redis
import sys
sys.path.append('main')
from main.MU_conf import MU_FlaskConfig
__version__='0.0.1'
bootstrap=Bootstrap()
mail=Mail()
moment=Moment()
login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
r = redis.Redis(host="localhost", port=6379, db=0)
def create_app():
    app=Flask(__name__)
    app.config.from_object(MU_FlaskConfig)
    MU_FlaskConfig.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.config['SECRET_KEY']='1235789'
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app
