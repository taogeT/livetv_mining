#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from lxml import etree

from .. import redis
from . import request_headers

import requests

REDIS_PROXY_LIST = 'proxy_http_ips' # 存储内容 http://xxx.xxx.xxx.xxx:yy
REDIS_PROXY_PAGE = 'proxy_http_page'
REDIS_PROXY_MIN = 10
REDIS_PROXY_MAX = 1000


def search_proxy():
    """ 从外部抓取代理IP，测试用例站点 """
    proxy_url = 'http://www.kuaidaili.com/free/inha/{}/'
    proxy_headers = dict(request_headers, Host='www.kuaidaili.com', Referer='http://www.kuaidaili.com')
    while redis.scard(REDIS_PROXY_LIST) < REDIS_PROXY_MAX:
        proxy_page = redis.incr(REDIS_PROXY_PAGE)
        resp = requests.get(proxy_url.format(proxy_page), headers=proxy_headers)
        listbody = etree.HTML(resp.content).xpath('//div[@id=\'list\']/table/tbody')[0]
        for ip_tr_element in listbody.xpath('./tr'):
            proxyip = ip_tr_element.xpath('./td[@data-title=\'IP\']')[0].text
            proxyport = ip_tr_element.xpath('./td[@data-title=\'PORT\']')[0].text
            proxytype = ip_tr_element.xpath('./td[@data-title=\'类型\']')[0].text.lower()
            redis.sadd(REDIS_PROXY_LIST, '{}://{}:{}'.format(proxytype, proxyip, proxyport))


def check_proxy(proxies):
    resp = requests.get('http://bing.com', headers=request_headers, proxies=proxies)
    return resp.status_code == requests.codes.ok


def get_proxy_http():
    try:
        proxyip = None
        while True:
            if redis.scard(REDIS_PROXY_LIST) <= REDIS_PROXY_MIN:
                search_proxy()
                continue
            proxyip = redis.spop(REDIS_PROXY_LIST).decode('utf-8')
            print(proxyip)
            if not check_proxy({'http': proxyip}):
                continue
            return proxyip
    finally:
        if proxyip:
            redis.sadd(REDIS_PROXY_LIST, proxyip)
