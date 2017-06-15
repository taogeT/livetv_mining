# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom
from ..items import OnceItem

import json


class QuanminOnceSpider(Spider):
    name = 'panda_once'
    allowed_domains = ['panda.tv']
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
        base_query = session.query(LiveTVRoom).join(LiveTVSite).filter(LiveTVSite.code == 'panda')\
                            .filter(LiveTVRoom.crawl_date <= utc_date)
        for room in base_query.filter(LiveTVRoom.crawl_date > utc_date - timedelta(days=30)):
            meta_info = {
                'room_url': room.url,
                'host': room.host,
            }
            yield Request('http://www.panda.tv/api_room?roomid=' + room.office_id, callback=self.parse, meta=meta_info)
        session.close()

    def parse(self, response):
        resp_info = json.loads(response.text)
        if resp_info['errno'] == 0:
            main_info = resp_info['data']
            yield OnceItem({
                'room_url': response.meta['room_url'],
                'channel_name': main_info['roominfo']['classification'],
                'host': response.meta['host'],
                'followers': int(main_info['roominfo']['fans']),
                'start_time': datetime.utcfromtimestamp(main_info['roominfo']['start_time']),
                'donate': main_info['hostinfo']['bamboos'],
                'description': main_info['roominfo']['details'],
                'announcement': main_info['roominfo']['bulletin']
            })
