# -*- coding: UTF-8 -*-
from flask import Blueprint

weixin = Blueprint('weixin', __name__)

from . import token
