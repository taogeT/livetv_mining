# -*- coding: UTF-8 -*-
from flask import Blueprint

webpage = Blueprint('webpage', __name__, template_folder='templates')

from . import views
