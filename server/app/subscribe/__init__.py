# -*- coding: UTF-8 -*-
from flask import Blueprint

subscribe = Blueprint('subscribe', __name__, template_folder='templates')

from . import views
