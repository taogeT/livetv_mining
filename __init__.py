# -*- coding: UTF-8 -*-
from flask import Blueprint

crawler = Blueprint('crawler', __name__, template_folder='templates', static_folder='static')

from . import views

request_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36',
}

from .instance import douyu, panda, zhanqi

config = {
    'douyu': douyu.DouyuCrawler,
    'panda': panda.PandaCrawler,
    'zhanqi': zhanqi.ZhanqiCrawler
}
