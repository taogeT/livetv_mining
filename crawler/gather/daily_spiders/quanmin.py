# -*- coding: utf-8 -*-
from scrapy import Spider
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..models import LiveTVSite, LiveTVRoom, LiveTVRoomPresent, DAILY_DATE_FORMAT
from ..items import DailyItem

import numpy


class QuanminDailySpider(Spider):
    name = 'quanmin_daily'
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
                                    func.array_agg(LiveTVRoomPresent.online).label('online_list'))\
            .join(LiveTVSite, LiveTVRoom, LiveTVRoomPresent)\
            .filter(LiveTVRoomPresent.crawl_date_format == summary_utc.strftime(DAILY_DATE_FORMAT))\
            .group_by(LiveTVSite.id, LiveTVRoom.id, LiveTVRoom.url, LiveTVRoomPresent.crawl_date_format)
        for group_row in db_query:
            meta_info = {
                'site_id': group_row.site_id,
                'room_id': group_row.room_id,
                'summary_date': group_row.summary_date,
                'online': numpy.median(group_row.online_list)
            }
            room = self.session.query(LiveTVRoom).filter_by(id=meta_info['room_id']).one_or_none()
            if room:
                yield DailyItem(site_id=group_row.site_id, room_id=group_row.room_id,
                                summary_date=group_row.summary_date, online=numpy.median(group_row.online_list),
                                followers=room.followers, description=room.description, announcement=room.announcement,
                                fallback=False)
        db_session.close()

    def parse(self, response):
        raise NotImplementedError
