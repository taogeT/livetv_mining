# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask_restful import Api, Resource

rest = Blueprint('rest', __name__)
rest_api = Api(rest)

from .main import *
