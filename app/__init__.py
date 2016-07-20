# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_celery import Celery
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_wtf import CsrfProtect
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
monkey.patch_all()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_pyfile('config.py', silent=True)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    redis.init_app(app, strict=True)
    csrf.init_app(app)

    from .crawler import crawler as crawler_blueprint
    app.register_blueprint(crawler_blueprint)

    from .webpage import webpage as webpage_blueprint
    app.register_blueprint(webpage_blueprint)

    celery.init_app(app)

    fhandler = FileHandler(app.config.get('FLASK_ERROR_LOGFILE', 'error.log'))
    fhandler.setLevel(logging.ERROR)
    fhandler.setFormatter(Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
    app.logger.addHandler(fhandler)

    return app
