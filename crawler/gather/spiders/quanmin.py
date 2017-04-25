# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from datetime import datetime

from ..items import ChannelItem, RoomItem

import json


class QuanminSpider(Spider):
    name = 'quanmin'
    allowed_domains = ['quanmin.tv']
    start_urls = [
        'https://www.quanmin.tv/json/categories/list.json'
    ]
    custom_settings = {
        'SITE': {
            'code': 'quanmin',
            'name': '全民',
            'description': '全民直播_做年轻人爱看的直播',
            'url': 'https://www.quanmin.tv',
            'image': 'https://static.quanmin.tv/static/v2/module/widget/header/img/logo_e00f8d6.svg',
            'show_seq': 7
        }
    }

    def parse(self, response):
        room_query_list = []
        for cjson in json.loads(response.text):
            yield ChannelItem({
                'office_id': str(cjson['id']),
                'short': cjson['slug'],
                'name': cjson['name'],
                'image': cjson['image'],
                'url': response.urljoin('/game/{}'.format(cjson['slug'])),
            })
            url = 'https://www.quanmin.tv/json/categories/{}/list{{}}.json'.format(cjson['slug'])
            room_query_list.append({'url': url, 'page': 0, 'channel': cjson['slug']})
        for room_query in room_query_list:
            yield Request(room_query['url'].format(''), callback=self.parse_room_list, meta=room_query)

    def parse_room_list(self, response):
        if response.text:
            room_list = json.loads(response.text)['data']
            if isinstance(room_list, list):
                for rjson in room_list:
                    image_url = rjson['thumb'][:rjson['thumb'].find('?')]
                    if image_url.startswith('http://'):
                        image_url = image_url.replace('http://', 'https://')
                    try:
                        start_time = datetime.utcfromtimestamp(float(rjson['start_time']))
                    except ValueError:
                        start_time = datetime.strptime(rjson['play_at'], '%Y-%m-%d %H:%M:%S')
                    yield RoomItem({
                        'office_id': rjson['uid'],
                        'name': rjson['title'],
                        'image': image_url,
                        'url': response.urljoin('/'+rjson['uid']),
                        'online': rjson['view'],
                        'host': rjson['nick'],
                        'channel': rjson['category_slug'],
                        'followers': rjson['follow'],
                        'description': rjson['intro'],
                        'announcement': rjson['announcement'],
                        'start_time': start_time
                    })
                if len(room_list) > 0:
                    next_meta = dict(response.meta, page=response.meta['page'] + 1)
                    yield Request(next_meta['url'].format('_'+str(next_meta['page'])),
                                  callback=self.parse_room_list, meta=next_meta)
