# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from ..items import ChannelItem, RoomItem

import json


class HuyaSpider(Spider):
    name = 'huya'
    allowed_domains = ['huya.com']
    start_urls = [
        'http://www.huya.com/g'
    ]
    custom_settings = {
        'SITE': {
            'code': 'huya',
            'name': '虎牙',
            'description': '虎牙直播-中国领先的互动直播平台',
            'url': 'http://www.huya.com',
            'image': 'http://a.dwstatic.com/huya/main/img/logo.png',
            'show_seq': 2
        }
    }

    def parse(self, response):
        room_query_list = []
        for a_element in response.xpath('//li[@class="game-list-item"]/a'):
            url = a_element.xpath('@href').extract_first()
            short = url[url.rfind('/') + 1:]
            report_attr = json.loads(a_element.xpath('@report').extract_first())
            office_id = report_attr['game_id']
            img_element = a_element.xpath('img')[0]
            name = img_element.xpath('@title').extract_first()
            image = img_element.xpath('@data-original').extract_first()
            yield ChannelItem({
                'office_id': office_id,
                'short': short,
                'name': name,
                'image': image,
                'url': url
            })
            url = 'http://www.huya.com/cache.php?m=LiveList&do=getLiveListByPage&tagAll=0&gameId={}'.format(office_id)
            room_query_list.append({'url': url, 'channel': short, 'page': 1})
        for room_query in room_query_list:
            yield Request('{}&page=1'.format(room_query['url']), callback=self.parse_room_list, meta=room_query)

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data']['datas']
        if isinstance(room_list, list):
            for rjson in room_list:
                yield RoomItem({
                    'office_id': rjson['privateHost'],
                    'name': rjson['introduction'],
                    'image': rjson['screenshot'],
                    'url': response.urljoin(rjson['privateHost']),
                    'online': int(rjson['totalCount']) if rjson['totalCount'].isdigit() else 0,
                    'host': rjson['nick'],
                    'channel': rjson['gameHostName']
                })
            if len(room_list) > 0:
                next_meta = dict(response.meta, page=response.meta['page'] + 1)
                yield Request('{}&page={}'.format(next_meta['url'], str(next_meta['page'])),
                              callback=self.parse_room_list, meta=next_meta)
