# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from datetime import datetime

from ..items import ChannelItem, RoomItem

import json


class HuamaoSpider(Spider):
    name = 'huomao'
    allowed_domains = ['huomao.com']
    start_urls = [
        'https://www.huomao.com/game'
    ]
    custom_settings = {
        'SITE': {
            'code': 'huomao',
            'name': '火猫',
            'description': '网络游戏直播大全-火猫直播',
            'url': 'https://www.huomao.com',
            'image': 'https://www.huomao.com/static/web/images/logo.jpg',
            'show_seq': 8
        }
    }

    def parse(self, response):
        for a_element in response.xpath('//div[@class="game-smallbox"]/a'):
            url = a_element.xpath('@href').extract_first()
            img_element = a_element.xpath('img')[0]
            image = img_element.xpath('@data-original').extract_first()
            if 'channellabel/showChannelLabel' in url:
                continue
            elif 'gamecollection/gameCollectionDetail' in url:
                yield Request(url, callback=self.parse_collection)
            else:
                short = url[url.rfind('/') + 1:]
                name = a_element.xpath('p/text()').extract_first()
                yield ChannelItem({
                    'short': short,
                    'name': name,
                    'image': image,
                    'url': url
                })
                url = 'https://www.huomao.com/channels/channel.json?page_size=120&game_url_rule={}'.format(short)
                yield Request('{}&page=1'.format(url), callback=self.parse_room_list, meta={'url': url, 'page': 1})

    def parse_collection(self, response):
        for a_element in response.xpath('//div[@id="game_label"]/li/a')[1:]:
            short = a_element.xpath('@id').extract_first()
            yield ChannelItem({
                'short': short,
                'name': a_element.xpath('text()').extract_first(),
                'url': response.urljoin('/channel/{}'.format(short))
            })
            url = 'https://www.huomao.com/channels/channel.json?page_size=120&game_url_rule={}'.format(short)
            yield Request('{}&page=1'.format(url), callback=self.parse_room_list, meta={'url': url, 'page': 1})

    def parse_room_list(self, response):
        room_list = json.loads(response.text)['data'].get('channelList', None)
        if isinstance(room_list, list):
            for rjson in room_list:
                if int(rjson['is_live']) == 0:
                    break
                item = RoomItem({
                    'office_id': rjson['id'],
                    'name': rjson['channel'],
                    'image': rjson['image'],
                    'url': response.urljoin('/' + rjson['room_number']),
                    'host': rjson['nickname'],
                    'channel': rjson['game_url_rule'],
                    'online': rjson.get('originviews', self.format_views(rjson['views'])),
                    'followers': rjson.get('audienceNumber', None)
                })
                if 'live_last_start_time' in rjson:
                    item['start_time'] = datetime.utcfromtimestamp(float(rjson['live_last_start_time']))
                yield item
            else:
                if len(room_list) > 0:
                    next_meta = dict(response.meta, page=response.meta['page'] + 1)
                    yield Request('{}&page={}'.format(next_meta['url'], str(next_meta['page'])),
                                  callback=self.parse_room_list, meta=next_meta)

    def format_views(self, value):
        k_weight = 1
        if '万' in value:
            k_weight = 10000
            value = value.replace('万', '')
        return float(value.replace(',', '')) * k_weight
