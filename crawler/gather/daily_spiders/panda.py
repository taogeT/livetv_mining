# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom, LiveTVRoomPresent, DAILY_DATE_FORMAT
from ..items import DailyItem

import numpy
import json


class PandaDailySpider(Spider):
    name = 'panda_daily'
    allowed_domains = ['panda.tv']

    def start_requests(self):
        summary_utc = datetime.utcnow() - timedelta(days=1)
        db_engine = create_engine(self.settings.get('SQLALCHEMY_DATABASE_URI'))
        db_session = sessionmaker(bind=db_engine)()
        db_query = db_session.query(LiveTVSite.id.label('site_id'), LiveTVRoom.id.label('room_id'),
                                    LiveTVRoom.url.label('room_url'),
                                    LiveTVRoomPresent.crawl_date_format.label('summary_date'),
                                    func.array_agg(LiveTVRoomPresent.online).label('online_list')) \
            .join(LiveTVSite, LiveTVRoom, LiveTVRoomPresent) \
            .filter(LiveTVSite.code == 'panda') \
            .filter(LiveTVRoomPresent.crawl_date_format == summary_utc.strftime(DAILY_DATE_FORMAT)) \
            .group_by(LiveTVSite.id, LiveTVRoom.id, LiveTVRoom.url, LiveTVRoomPresent.crawl_date_format)
        for group_row in db_query:
            meta_info = {
                'site_id': group_row.site_id,
                'room_id': group_row.room_id,
                'summary_date': group_row.summary_date,
                'online': numpy.median(group_row.online_list)
            }
            yield Request('http://www.panda.tv/api_room?roomid=' + group_row.room_id, callback=self.parse,
                          meta=meta_info)
        db_session.close()

    def parse(self, response):
        resp_info = json.loads(response.text)
        if resp_info['errno'] == 0:
            room_info = resp_info['data']['roominfo']
            yield DailyItem({
                'site_id': response.meta['site_id'],
                'room_id': response.meta['room_id'],
                'summary_date': response.meta['summary_date'],
                'online': response.meta['online'],
                'followers': room_info['fans'],
                'description': room_info['details'],
                'announcement': room_info['bulletin'],
                'fallback': True
            })
