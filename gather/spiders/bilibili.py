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
        for a_element in response.xpath('//div[{}]/a'.format(' and '.join(panel_xpath)))[1:-2]:
            url = a_element.xpath('@href').extract_first()
            short = url[1:]
            name = a_element.xpath('div/text()').extract_first()
            yield ChannelItem({'short': short, 'name': name, 'url': response.urljoin(url)})
            self.logger.debug('遍历频道 {}...'.format(name))
            url = 'http://live.bilibili.com/area/liveList?order=online&area={}'.format(short)
            yield Request('{}&page=1'.format(url), callback=self.parse_room_list,
                          meta={'url': url, 'channel': short, 'area': short, 'page': 1})

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']
        for rjson in room_list:
            yield RoomItem({
                'office_id': rjson['roomid'],
                'name': rjson['title'],
                'image': rjson['cover'],
                'url': response.urljoin(rjson['link']),
                'online': rjson['online'],
                'channel': response.meta['channel'],
            })
        if len(room_list) > 0:
            next_meta = dict(response.meta, page=response.meta['page'] + 1)
            yield Request('{}&page={}'.format(next_meta['url'], str(next_meta['page'])),
                          callback=self.parse_room_list, meta=next_meta)
