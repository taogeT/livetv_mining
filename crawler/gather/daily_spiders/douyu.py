# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom, LiveTVRoomPresent, DAILY_DATE_FORMAT
from ..items import DailyItem

import numpy
import json


class DouyuDailySpider(Spider):
    name = 'douyu_daily'
    allowed_domains = ['douyucdn.cn', 'douyu.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'gather.pipelines.StatisticPipeline': 300
        }
    }

    def start_requests(self):
        summary_utc = datetime.utcnow() - timedelta(days=1)
        db_engine = create_engine(self.settings.get('SQLALCHEMY_DATABASE_URI'))
        db_session = sessionmaker(bind=db_engine)()
        db_query = db_session.query(LiveTVSite.id.label('site_id'), LiveTVRoom.id.label('room_id'),
                                    LiveTVRoom.url.label('room_url'),
                                    LiveTVRoomPresent.crawl_date_format.label('summary_date'),
                                    func.array_agg(LiveTVRoomPresent.online).label('online_list')) \
            .join(LiveTVSite, LiveTVRoom, LiveTVRoomPresent) \
            .filter(LiveTVSite.code == 'douyu') \
            .filter(LiveTVRoomPresent.crawl_date_format == summary_utc.strftime(DAILY_DATE_FORMAT)) \
            .group_by(LiveTVSite.id, LiveTVRoom.id, LiveTVRoom.url, LiveTVRoomPresent.crawl_date_format)
        for group_row in db_query:
            meta_info = {
                'site_id': group_row.site_id,
                'room_id': group_row.room_id,
                'summary_date': group_row.summary_date,
                'online': numpy.median(group_row.online_list)
            }
            yield Request('http://open.douyucdn.cn/api/RoomApi/room/' + group_row.room_id, callback=self.parse,
                          meta=meta_info)
        db_session.close()

    def parse(self, response):
        resp_info = json.loads(response.text)
        if resp_info['error'] == 0:
            room_info = resp_info['data']
            meta_info = dict(response.meta, followers=room_info['fans_num'])
            yield Request('https://m.douyu.com/html5/live?roomId=' + meta_info['room_id'],
                          callback=self.parse_html5, meta=meta_info)

    def parse_html5(self, response):
        resp_info = json.loads(response.text)
        if resp_info['error'] == 0:
            room_info = resp_info['data']
            yield DailyItem({
                'site_id': response.meta['site_id'],
                'room_id': response.meta['room_id'],
                'summary_date': response.meta['summary_date'],
                'online': response.meta['online'],
                'followers': response.meta['followers'],
                'description': '',
                'announcement': room_info['show_details'],
                'fallback': True
            })
