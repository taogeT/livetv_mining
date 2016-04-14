# -*- coding: UTF-8 -*-
from flask import current_app, Blueprint
from selenium import webdriver
from selenium.webdriver.phantomjs.webdriver import DesiredCapabilities
from functools import reduce

from ..models import LiveTVSite

import sys
import time

crawler = Blueprint('crawler', __name__)


def get_webdriver_client():
    desiredcap = DesiredCapabilities.PHANTOMJS
    desiredcap['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
    command_line_args = ['--disk-cache=true', '--load-images=false']
    driver = webdriver.PhantomJS(desired_capabilities=desiredcap, service_args=command_line_args)
    driver.set_page_load_timeout(30)
    return driver


from . import douyu, zhanqi, panda, views


def crawl_channel(site_url, inner_func):
    site = LiveTVSite.query.filter_by(url=site_url, valid=True).one()
    finished = False
    while not finished:
        finished = inner_func(site)
        time.sleep(5)


def crawl_room(site_url, inner_func, channel_url=None):
    site = LiveTVSite.query.filter_by(url=site_url, valid=True).one()
    channels = site.channels.filter_by(valid=True)
    if channel_url:
        channels = channels.filter_by(url=channel_url)
    channels = channels.all()
    while len(channels) > 0:
        channel = channels.pop(0)
        if not inner_func(channel):
            channels.append(channel)


class LiveTVCrawler(object):
    ''' 爬虫操作 '''
    def __init__(self, **kwargs):
        sites = LiveTVSite.query.filter_by(valid=True)
        if len(kwargs) > 0:
            sites = sites.filter_by(**kwargs)
        self.crawlers = {'channel': [], 'room': []}
        for site in sites.all():
            site_module_name = '{}.{}'.format(__name__, site.name)
            site_module = sys.modules.get(site_module_name)
            site_param = {'site_url': site.url}
            if site_module:
                current_app.logger.info('Module {} found.'.format(site_module_name))
                crawl_channel_inner = getattr(site_module, 'crawl_channel_inner', None)
                if crawl_channel_inner:
                    channel_param = dict(site_param, inner_func=crawl_channel_inner)
                    self.crawlers['channel'].append((crawl_channel, channel_param))
                else:
                    current_app.logger.error('Method crawl_channel does not exist.')
                crawl_room_inner = getattr(site_module, 'crawl_room_inner', None)
                if crawl_room_inner:
                    room_param = dict(site_param, inner_func=crawl_room_inner)
                    self.crawlers['room'].append((crawl_room, room_param))
                else:
                    current_app.logger.error('Method crawl_room does not exist.')
            else:
                current_app.logger.error('Module {} does not exist.'.format(site_module_name))

    def channel(self):
        ''' 频道爬虫启动 '''
        for method, kwargs in self.crawlers['channel']:
            method(**kwargs)

    def room(self, channel_url=None):
        ''' 房间爬虫启动 '''
        for method, kwargs in self.crawlers['room']:
            kwargs = dict(kwargs, channel_url=channel_url)
            method(**kwargs)
