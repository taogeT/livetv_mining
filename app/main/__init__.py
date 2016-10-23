# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restful import Api, Resource

main = Blueprint('main', __name__, template_folder='templates')
main_api = Api(main, prefix='/rest')

from . import views
from .apis import *
