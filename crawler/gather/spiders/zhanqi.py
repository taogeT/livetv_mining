# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from ..items import ChannelItem, RoomItem

import json


class ZhanqiSpider(Spider):
    name = 'zhanqi'
    allowed_domains = ['zhanqi.tv']
    start_urls = [
        'https://www.zhanqi.tv/api/static/game.lists/300-1.json'
    ]
    custom_settings = {
        'SITE': {
            'code': 'zhanqi',
            'name': '战旗',
            'description': '战旗直播_高清流畅的游戏直播平台',
            'url': 'https://www.zhanqi.tv',
            'image': 'https://static.zhanqi.tv/assets/web/static/i/index/skin/logo.png',
            'show_seq': 6
        }
    }

    def parse(self, response):
        room_query_list = []
        for cjson in json.loads(response.text)['data']['games']:
            yield ChannelItem({
                'office_id': cjson['id'],
                'short': cjson['gameKey'],
                'name': cjson['name'],
                'image': cjson['spic'],
                'url': response.urljoin(cjson['url'])
            })
            url = 'https://www.zhanqi.tv/api/static/game.lives/{}/110-{{}}.json'.format(cjson['id'])
            room_query_list.append({'url': url, 'channel': cjson['gameKey'], 'page': 1})
        for room_query in room_query_list:
            yield Request(room_query['url'].format(str(room_query['page'])), callback=self.parse_room_list,
                          meta=room_query)

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']['rooms']
        if isinstance(room_list, list):
            for rjson in room_list:
                yield RoomItem({
                    'office_id': rjson['id'],
                    'name': rjson['title'],
                    'image': rjson['bpic'],
                    'url': response.urljoin(rjson['url']),
                    'online': int(rjson['online']) if rjson['online'].isdigit() else 0,
                    'host': rjson['nickname'],
                    'channel': response.meta['channel']
                })
            if len(room_list) > 0:
                next_meta = dict(response.meta, page=response.meta['page'] + 1)
                yield Request(next_meta['url'].format(str(next_meta['page'])), callback=self.parse_room_list,
                              meta=next_meta)
