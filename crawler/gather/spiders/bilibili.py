# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from ..items import ChannelItem, RoomItem

import json


class BilibiliSpider(Spider):
    name = 'bilibili'
    allowed_domains = ['bilibili.com']
    start_urls = [
        'http://live.bilibili.com/area/live'
    ]
    custom_settings = {
        'SITE': {
            'code': 'bilibili',
            'name': '哔哩哔哩',
            'description': '哔哩哔哩-关注ACG直播互动平台',
            'url': 'http://live.bilibili.com',
            'image': 'http://static.hdslb.com/live-static/common/images/logo/logo-150-cyan.png',
            'show_seq': 2,
        }
    }

    def parse(self, response):
        panel_class = ['live-top-nav-panel', 'live-top-hover-panel']
        panel_xpath = ['contains(@class, "{}")'.format(pclass) for pclass in panel_class]
        room_query_list = []
        for a_element in response.xpath('//div[{}]/a'.format(' and '.join(panel_xpath)))[1:-2]:
            url = a_element.xpath('@href').extract_first()
            short = url[url.rfind('/') + 1:]
            name = a_element.xpath('div/text()').extract_first()
            yield ChannelItem({'short': short, 'name': name, 'url': response.urljoin(url)})
            self.logger.debug('遍历频道 {}...'.format(name))
            url = 'http://live.bilibili.com/area/liveList?area={}&order=online'.format(short)
            room_query_list.append({'url': url, 'channel': short, 'area': short, 'page': 1})
        for room_query in room_query_list:
            yield Request('{}&page=1'.format(room_query['url']), callback=self.parse_room_list,
                          meta=room_query)

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']
        if isinstance(room_list, list):
            for rjson in room_list:
                if isinstance(rjson['online'], int):
                    yield RoomItem({
                        'office_id': str(rjson['roomid']),
                        'name': rjson['title'],
                        'image': rjson['cover'],
                        'url': response.urljoin(rjson['link']),
                        'online': rjson['online'],
                        'host': rjson['uname'],
                        'channel': response.meta['channel'],
                    })
            if len(room_list) > 0:
                next_meta = dict(response.meta, page=response.meta['page'] + 1)
                yield Request('{}&page={}'.format(next_meta['url'], str(next_meta['page'])),
                              callback=self.parse_room_list, meta=next_meta)
