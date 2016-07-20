# -*- coding: UTF-8 -*-
from flask import Blueprint

main = Blueprint('main', __name__, template_folder='templates')

from . import views
