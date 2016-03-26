# -*- coding: UTF-8 -*-
from datetime import datetime
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy

from config import config

import os

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .crawler import crawler as crawler_blueprint
    app.register_blueprint(crawler_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .main.views import index
    app.add_url_rule('/', 'main.root', index)

    return app
