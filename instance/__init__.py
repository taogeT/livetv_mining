# -*- coding: UTF-8 -*-
from requests.exceptions import ProxyError, ConnectionError

from ... import db
from .. import crawler
from ..models import LiveTVSite
from ..proxy import get_proxy_http
from ..exceptions import SiteConfigError

import requests
import importlib
import types
import random
import gevent


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

    def _get_response(self, url, params=None, use_proxy=False):
        proxies = {}
        if use_proxy:
            proxy_http_ip = get_proxy_http()
            if proxy_http_ip:
                proxies['http'] = proxy_http_ip
        gevent.sleep(self._interval_seconds())
        try:
            return requests.get(url, params=params, headers=self.request_headers, proxies=proxies)
        except ProxyError:
            return requests.get(url, params=params, headers=self.request_headers)
        except ConnectionError:
            return None

    def _interval_seconds(self):
        return random.randint(1, 5)
