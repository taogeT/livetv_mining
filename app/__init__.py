# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_celery import Celery
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
celery = Celery()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_pyfile('config.py', silent=True)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .crawler import crawler as crawler_blueprint
    app.register_blueprint(crawler_blueprint, url_prefix='/crawler')

    from .weixin import weixin as weixin_blueprint
    app.register_blueprint(weixin_blueprint, url_prefix='/weixin')

    celery.init_app(app)

    from .views import index, about
    app.add_url_rule('/', endpoint='index', view_func=index)
    app.add_url_rule('/about', endpoint='about', view_func=about)

    return app
