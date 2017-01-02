# -*- coding: UTF-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from flask_login import LoginManager
from flask_cors import CORS
from gevent import monkey

db = SQLAlchemy()
oauth = OAuth()
login_manager = LoginManager()
cors = CORS()
monkey.patch_all()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)

    from .rest import rest as rest_blueprint
    app.register_blueprint(rest_blueprint, url_prefix='/rest')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    login_manager.login_view = '/login'

    return app
