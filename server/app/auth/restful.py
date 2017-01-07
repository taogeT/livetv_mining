# -*- coding: UTF-8 -*-
from flask_restful import Api, Resource
from flask_login import login_required

from . import auth

auth_api = Api(auth)


@auth_api.resource('/verify')
class Verify(Resource):

    method_decorators = [login_required]

    def get(self):
        return {'username': g.user.username}


@auth_api.resource('/user')
class User(Resource):

    method_decorators = [login_required]

    def get(self):
        return g.user.to_dict()
