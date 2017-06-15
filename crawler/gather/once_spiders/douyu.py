# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom
from ..items import OnceItem

import json


class DouyuOnceSpider(Spider):
    name = 'douyu_once'
    allowed_domains = ['douyucdn.cn', 'douyu.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'gather.pipelines.HardDiskPipeline': 300
        }
    }

    def start_requests(self):
        db_engine = create_engine(self.settings.get('SQLALCHEMY_DATABASE_URI'))
        db_session_maker = sessionmaker(bind=db_engine)
        session = db_session_maker()
        utc_date = datetime.utcnow()
        base_query = session.query(LiveTVRoom).join(LiveTVSite).filter(LiveTVSite.code == 'douyu') \
            .filter(LiveTVRoom.crawl_date <= utc_date)
        for room in base_query.filter(LiveTVRoom.crawl_date > utc_date - timedelta(days=30)):
            meta_info = {
                'room_url': room.url,
                'host': room.host,
            }
            yield Request('http://open.douyucdn.cn/api/RoomApi/room/' + room.office_id, callback=self.parse,
                          meta=meta_info)
        session.close()

    def parse(self, response):
        resp_json = json.loads(response.text)
        if resp_json['error'] == 0:
            room_json = resp_json['data']
            # maybe some filter
            meta_info = dict(response.meta, channel_name=room_json['cate_name'], start_time=room_json['start_time'],
                             followers=room_json['fans_num'], donate=room_json['owner_weight'])
            yield Request('https://m.douyu.com/html5/live?roomId=' + room_json['room_id'], callback=self.parse_html5,
                          meta=meta_info)

    def parse_html5(self, response):
        resp_json = json.loads(response.text)
        if resp_json['error'] == 0:
            room_json = resp_json['data']
            yield OnceItem({
                'room_url': response.meta['room_url'],
                'channel_name': response.meta['channel_name'],
                'host': response.meta['host'],
                'followers': response.meta['followers'],
                'start_time': response.meta['start_time'],
                'donate': response.meta['donate'],
                'announcement': room_json['show_details']
            })
