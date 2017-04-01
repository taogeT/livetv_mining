# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from ..items import ChannelItem, RoomItem

import json


class PandaSpider(Spider):
    name = 'panda'
    allowed_domains = ['panda.tv']
    start_urls = [
        'http://api.m.panda.tv/ajax_get_all_subcate'
    ]
    custom_settings = {
        'SITE': {
            'code': 'panda',
            'name': '熊猫',
            'description': '熊猫直播_泛娱乐直播平台',
            'url': 'http://www.panda.tv',
            'image': 'http://i9.pdim.gs/b2a97149ec43dfc95eb177508af29f6c.png',
            'show_seq': 4
        }
    }

    def parse(self, response):
        room_query_list = []
        for cjson in json.loads(response.text)['data']:
            yield ChannelItem({
                'short': cjson['ename'],
                'name': cjson['cname'],
                'image': cjson['img'],
                'url': 'http://www.panda.tv/cate/' + cjson['ename']
            })
            url = 'http://www.panda.tv/ajax_sort?classification={}&pagenum=120'.format(cjson['ename'])
            room_query_list.append({'url': url, 'channel': cjson['ename'], 'pageno': 1})
        for room_query in room_query_list:
            yield Request('{}&pageno=1'.format(room_query['url']), callback=self.parse_room_list, meta=room_query)

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']['items']
        if isinstance(room_list, list):
            for rjson in room_list:
                yield RoomItem({
                    'office_id': rjson['id'],
                    'name': rjson['name'],
                    'image': rjson['pictures']['img'],
                    'url': response.urljoin(rjson['id']),
                    'online': int(rjson['person_num']) if rjson['person_num'].isdigit() else 0,
                    'host': rjson['userinfo']['nickName'],
                    'channel': response.meta['channel']
                })
            if len(room_list) > 0:
                next_meta = dict(response.meta, pageno=response.meta['pageno'] + 1)
                yield Request('{}&pageno={}'.format(next_meta['url'], str(next_meta['pageno'])),
                              callback=self.parse_room_list, meta=next_meta)
