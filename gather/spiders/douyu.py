# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from ..items import ChannelItem, RoomItem

import json


class DouyuSpider(Spider):
    name = 'douyu'
    allowed_domains = ['douyucdn.cn']
    start_urls = [
        'http://open.douyucdn.cn/api/RoomApi/game'
    ]
    custom_settings = {
        'SITE': {
            'code': 'douyu',
            'name': '斗鱼',
            'description': '斗鱼-全民直播平台',
            'url': 'http://www.douyu.com',
            'image': 'http://staticlive.douyutv.com/common/douyu/images/logo_zb.png',
            'show_seq': 1,
        }
    }

    def parse(self, response):
        for cjson in json.loads(response.text)['data']:
            yield ChannelItem({
                'office_id': cjson['cate_id'],
                'short': cjson['short_name'],
                'name': cjson['game_name'],
                'image': cjson['game_src'],
                'url': cjson['game_url'],
            })
            self.logger.debug('遍历频道 {}...'.format(cjson['game_name']))
            url = 'http://open.douyucdn.cn/api/RoomApi/live/{}?limit=100'.format(cjson['short_name'])
            yield Request('{}&offset=0'.format(url), callback=self.parse_room_list,
                          meta={'url': url, 'offset': 0, 'channel': cjson['short_name']})

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']
        for rjson in room_list:
            yield RoomItem({
                'office_id': rjson['room_id'],
                'name': rjson['room_name'],
                'image': rjson['room_src'],
                'url': rjson['url'],
                'online': rjson['online'],
                'host': rjson['nickname'],
                'channel': response.meta['channel'],
            })
        if len(room_list) > 0:
            next_meta = dict(response.meta, offset=response.meta['offset'] + len(room_list))
            yield Request('{}&offset={}'.format(next_meta['url'], str(next_meta['offset'])),
                          callback=self.parse_room_list, meta=next_meta)
