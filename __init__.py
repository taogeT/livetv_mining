# -*- coding: UTF-8 -*-
from flask import Blueprint

crawler = Blueprint('crawler', __name__, template_folder='templates', static_folder='static')

from . import views

from .instance import douyu, panda, zhanqi, twitch

config = {
    'douyu': douyu.DouyuCrawler,
    'panda': panda.PandaCrawler,
    'zhanqi': zhanqi.ZhanqiCrawler,
    #'twitch': twitch.TwitchCrawler,
}
