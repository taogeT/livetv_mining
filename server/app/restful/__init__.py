# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restful import Api, Resource

restful = Blueprint('restful', __name__)
restful_api = Api(restful)

from .main import *
from .user import *
from .subscribe import *
