# -*- coding: UTF-8 -*-
from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates')

from . import views
from . import github
