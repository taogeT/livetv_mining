# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_celery import Celery
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_wtf import CsrfProtect
from flask_oauthlib.client import OAuth
from flask_login import LoginManager
from gevent import monkey
from logging import FileHandler, Formatter

from config import config

import logging

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
celery = Celery()
redis = FlaskRedis()
csrf = CsrfProtect()
oauth = OAuth()
login_manager = LoginManager()
monkey.patch_all()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_pyfile('config.py', silent=True)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    redis.init_app(app, strict=True)
    csrf.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)

    from .crawler import crawler as crawler_blueprint
    app.register_blueprint(crawler_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .subscribe import subscribe as subscribe_blueprint
    app.register_blueprint(subscribe_blueprint, url_prefix='/subscribe')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    celery.init_app(app)
    login_manager.login_view = 'auth.login'

    from .views import about
    app.add_url_rule('/', endpoint='index', view_func=main.views.sites_index)
    app.add_url_rule('/about', endpoint='about', view_func=about)

    fhandler = FileHandler(app.config.get('FLASK_ERROR_LOGFILE', 'error.log'))
    fhandler.setLevel(logging.ERROR)
    fhandler.setFormatter(Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    app.logger.addHandler(fhandler)

    return app
