# -*- coding: UTF-8 -*-
from flask import Blueprint

from .. import csrf

api = Blueprint('api', __name__)

from . import views

csrf.exempt(api)
