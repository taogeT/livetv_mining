# -*- coding: UTF-8 -*-
from flask import g
from flask_login import login_required

from . import restful_api as user_api, Resource


@user_api.resource('/user/verify')
class Verify(Resource):

    method_decorators = [login_required]

    def get(self):
        return {'username': g.user.username}


@user_api.resource('/user')
class User(Resource):

    method_decorators = [login_required]

    def get(self):
        return g.user.to_dict()
