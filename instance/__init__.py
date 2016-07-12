# -*- coding: UTF-8 -*-
from flask import current_app, copy_current_request_context
from requests.exceptions import ProxyError, ConnectionError
from gevent.pool import Pool as GeventPool
from gevent.queue import Queue as GeventQueue

from ... import db
from .. import crawler
from ..models import LiveTVSite
from ..proxy import get_proxy_http
from ..exceptions import SiteConfigError

import requests
import importlib
import types
import random
import logging

logging.getLogger('requests').setLevel(logging.WARNING)


class LiveTVCrawler(object):
    """ 爬虫操作 """
    def __init__(self, site_code):
        module = importlib.import_module('.'.join([crawler.import_name, 'instance', site_code]))
        for key in module.__all__:
            if not hasattr(self, key):
                value = getattr(module, key)
                if isinstance(value, types.FunctionType):
                    setattr(self, key, types.MethodType(value, self))
                else:
                    setattr(self, key, value)
        self.site = self._get_site(site_code)
        if not self.site:
            raise SiteConfigError('Can not get site info from config')

    def _get_site(self, site_code):
        """ 获得站点信息，返回数据对象 Override by subclass """
        site = LiveTVSite.query.filter_by(code=site_code).one_or_none()
        if not site and hasattr(self, 'settings'):
            site = LiveTVSite(**self.settings)
            db.session.add(site)
            db.session.commit()
        return site if site and site.valid else None

    def _get_response(self, url, params=None, headers=None, use_proxy=False, to_json=True):
        reqkwargs = {
            'timeout': 30,
            'params': params,
            'headers': headers if headers else self.request_headers
        }
        if use_proxy:
            proxy_http_ip = get_proxy_http()
            if proxy_http_ip:
                reqkwargs['proxies'] = {'http': proxy_http_ip}
        try_entries = 3
        for i in range(try_entries):
            try:
                resp = requests.get(url, **reqkwargs)
                if resp.status_code != requests.codes.ok:
                    error_msg = '调用接口{}失败: 状态{}'.format(url, resp.status_code)
                    current_app.logger.error(error_msg)
                    raise ValueError(error_msg)
                return resp.json() if to_json else resp.text
            except (ConnectionError, ProxyError) as e:
                if i == try_entries:
                    current_app.logger.error(repr(e))
                    raise e
                continue
            except ValueError as e:
                current_app.logger.error(repr(e))
                raise e

    def _interval_seconds(self):
        return random.randint(1, 3)

    def _gevent_pool_search(self, searchlist, searchfunc):
        gpool = GeventPool(current_app.config.get('GEVENT_POOL_SIZE', 10))
        gqueue = GeventQueue(current_app.config.get('GEVENT_QUEUE_SIZE', 200))
        def init_gevent_pool():
            for search in searchlist:
                gpool.wait_available()
                gpool.spawn(copy_current_request_context(searchfunc), search, gqueue)

        gpool.spawn(copy_current_request_context(init_gevent_pool))
        return gpool, gqueue
