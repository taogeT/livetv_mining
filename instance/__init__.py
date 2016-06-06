# -*- coding: UTF-8 -*-
from gevent.pool import Pool as GeventPool
from flask import copy_current_request_context
from celery.exceptions import TimeoutError
from requests.exceptions import ProxyError

from .. import request_headers
from ..models import LiveTVChannel, LiveTVRoom

import requests
import gevent


class LiveTVCrawler(object):
    """ 爬虫操作 """

    def channels(self):
        """ 频道爬虫启动 """
        site = self._get_site()
        max_expires = 3
        while max_expires > 0:
            if self._channels(site):
                break
            else:
                max_expires -= 1

    def _get_site(self):
        """ 获得站点信息，返回数据对象 Override by subclass """

    def _get_proxy(self):
        """ 获得代理IP """
        return None
        #from ..tasks import get_proxy_http_task
        #try:
        #    asyncres = get_proxy_http_task.delay()
        #    return asyncres.get(timeout=10)
        #except TimeoutError:
        #    return None

    def _get_response(self, url, headers=request_headers):
        proxies = {}
        proxy_http_ip = self._get_proxy()
        if proxy_http_ip:
            proxies['http'] = proxy_http_ip
        try:
            return requests.get(url, headers=headers, proxies=proxies)
        except ProxyError:
            return requests.get(url, headers=headers)

    def _channels(self, site):
        """ 频道爬虫 Override by subclass """

    def rooms(self, channel_url=None):
        """ 房间爬虫启动 """
        channels = []
        if channel_url:
            channel_query = LiveTVChannel.query.filter_by(valid=True)
            if channel_url:
                channel_query = channel_query.filter_by(url=channel_url)
            channel = channel_query.one_or_none()
            if channel:
                channels.append(channel)
        else:
            site = self._get_site()
            channels.extend(site.channels.filter_by(valid=True).all())
        gpool = GeventPool(size=4)
        for channel in channels:
            gpool.spawn(copy_current_request_context(self._rooms), channel.id)
        gpool.join()

    def _rooms(self, channel):
        """ 房间爬虫 Override by subclass """

    def single_room(self, room_url=None):
        if room_url:
            room_query = LiveTVRoom.query
            if room_url:
                room_query = room_query.filter_by(url=room_url)
            room = room_query.one_or_none()
            if room:
                self._single_room(room)

    def _single_room(self, room):
        """ 单房间爬虫 Override by subclass """
