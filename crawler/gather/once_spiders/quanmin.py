# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom
from ..items import OnceItem

import json


class QuanminOnceSpider(Spider):
    name = 'quanmin_once'
    allowed_domains = ['quanmin.tv']
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
        base_query = session.query(LiveTVRoom).join(LiveTVSite).filter(LiveTVSite.code == 'quanmin')\
                            .filter(LiveTVRoom.crawl_date <= utc_date)
        for room in base_query.filter(LiveTVRoom.crawl_date > utc_date - timedelta(days=30)):
            meta_info = {
                'room_url': room.url,
                'host': room.host,
                'followers': room.followers,
                'start_time': room.start_time,
                'announcement': room.announcement
            }
            yield Request('http://www.quanmin.tv/json/rooms/{}/noinfo4.json'.format(room.office_id),
                          callback=self.parse, meta=meta_info)
        session.close()

    def parse(self, response):
        room_info = json.loads(response.text)
        if 'code' not in room_info:
            yield OnceItem({
                'room_url': response.meta['room_url'],
                'channel_name': room_info['category_name'],
                'host': response.meta['host'],
                'followers': response.meta['followers'],
                'start_time': response.meta['start_time'],
                'donate': str(room_info['weight']),
                'description': room_info['intro'],
                'announcement': response.meta['announcement'],
            })
