# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CsrfProtect
from flask_oauthlib.client import OAuth
from flask_login import LoginManager
from flask_vue import Vue
from gevent import monkey

bootstrap = Bootstrap()
db = SQLAlchemy()
csrf = CsrfProtect()
oauth = OAuth()
login_manager = LoginManager()
vue = Vue()
monkey.patch_all()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)

    bootstrap.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    vue.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .subscribe import subscribe as subscribe_blueprint
    app.register_blueprint(subscribe_blueprint, url_prefix='/subscribe')

    login_manager.login_view = 'auth.login'

    from .views import about
    app.add_url_rule('/', endpoint='index', view_func=main.views.room_index)
    app.add_url_rule('/about', endpoint='about', view_func=about)

    return app
