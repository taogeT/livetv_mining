# -*- coding: UTF-8 -*-
from flask import current_app, Blueprint
from selenium import webdriver
from selenium.webdriver.phantomjs.webdriver import DesiredCapabilities
from functools import reduce

from ..models import LiveTVSite, LiveTVChannel, LiveTVRoom
from ..models.crawler import LiveTVChannelData, LiveTVRoomData

import sys
import time

crawler = Blueprint('crawler', __name__)

from . import views


def get_webdriver_client():
    desiredcap = DesiredCapabilities.PHANTOMJS
    desiredcap['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
    command_line_args = ['--disk-cache=true', '--load-images=false']
    driver = webdriver.PhantomJS(desired_capabilities=desiredcap, service_args=command_line_args)
    driver.set_page_load_timeout(30)
    return driver


class LiveTVCrawler(object):
    ''' 爬虫操作 '''

    def channels(self):
        ''' 频道爬虫启动 '''
        site = self._get_site()
        max_expires = 3
        while max_expires > 0:
            if self._channels(site):
                break
            else:
                max_expires -= 1

    def _get_site(self):
        ''' 获得站点信息，返回数据对象 Override by subclass '''

    def _channels(self, site):
        ''' 频道爬虫 Override by subclass '''

    def rooms(self, channel_officeid=None, channel_url=None):
        ''' 房间爬虫启动 '''
        channels = []
        if channel_officeid or channel_url:
            channel_query = LiveTVChannel.query.filter_by(valid=True)
            if channel_officeid:
                channel_query = channel_query.filter_by(officeid=channel_officeid)
            if channel_url:
                channel_query = channel_query.filter_by(url=channel_url)
            channel = channel_query.one_or_none()
            if channel:
                channels.append(channel)
        else:
            site = self._get_site()
            channels.extend(site.channels.filter_by(valid=True).all())
        while len(channels) > 0:
            channel = channels.pop(0)
            if not self._rooms(channel):
                channels.append(channel)

    def _rooms(self, channel):
        ''' 房间爬虫 Override by subclass '''

    def single_room(self, room_officeid=None, room_url=None):
        if room_officeid or room_url:
            room_query = LiveTVRoom.query
            if room_officeid:
                room_query = room_query.filter_by(officeid=room_officeid)
            if room_url:
                room_query = room_query.filter_by(url=room_url)
            room = room_query.one_or_none()
            if room:
                self._single_room(room)

    def _single_room(self, room):
        ''' 单房间爬虫 Override by subclass '''


from . import douyu, panda , zhanqi, twitch

config = {
    'douyu': douyu.DouyuCrawler,
    'panda': panda.PandaCrawler,
    'zhanqi': zhanqi.ZhanqiCrawler,
    #'twitch': twitch.TwitchCrawler,
}

