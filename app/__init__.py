# -*- coding: UTF-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.celery import Celery

from config import config, Config

import os

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
celery = Celery()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    app.config.from_pyfile('config.py', silent=True)
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    celery.init_app(app)

    from .crawler import crawler as crawler_blueprint
    app.register_blueprint(crawler_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .main.views import index
    app.add_url_rule('/', 'main.root', index)

    return app
