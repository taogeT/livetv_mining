# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy.exceptions import CloseSpider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..items import ChannelItem, RoomItem, DailyItem
from ..models import LiveTVSite, LiveTVChannel, LiveTVRoom, LiveTVRoomPresent, LiveTVRoomDaily


class CurrentPipeline(object):

    def __init__(self, sqlalchemy_database_uri):
        self.engine = create_engine(sqlalchemy_database_uri)
        self.session_maker = sessionmaker(bind=self.engine)
        self.site = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlalchemy_database_uri=crawler.settings.get('SQLALCHEMY_DATABASE_URI')
        )

    def open_spider(self, spider):
        site_setting = spider.settings.get('SITE')
        if not site_setting:
            error_msg = 'Can not find the website configuration from settings.'
            spider.logger.error(error_msg)
            raise CloseSpider(error_msg)
        self.session = self.session_maker()
        site = self.session.query(LiveTVSite).filter(LiveTVSite.code == site_setting['code']).one_or_none()
        if not site:
            site = LiveTVSite(code=site_setting['code'], name=site_setting['name'],
                              description=site_setting['description'], url=site_setting['url'],
                              image=site_setting['image'], show_seq=site_setting['show_seq'])
            self.session.add(site)
            self.session.commit()
        self.site[site.code] = {'id': site.id, 'starttime': datetime.utcnow(), 'channels': {}}

    def close_spider(self, spider):
        site_dict = self.site[spider.settings.get('SITE')['code']]
        self.session.query(LiveTVRoom).filter(LiveTVRoom.crawl_date < site_dict['starttime']) \
                                 .filter(LiveTVRoom.site_id == site_dict['id']) \
                                 .update({'opened': False})
        self.session.commit()
        for channel in self.session.query(LiveTVChannel).filter(LiveTVChannel.site_id == site_dict['id']).all():
            channel.total = site_dict['channels'].get(channel.short, {}).get('total', 0)
            channel.valid = channel.total > 0
            self.session.add(channel)
            self.session.commit()
        self.session.close()

    def process_item(self, item, spider):
        site_dict = self.site[spider.settings.get('SITE')['code']]
        if isinstance(item, ChannelItem):
            channel = self.session.query(LiveTVChannel) \
                .filter(LiveTVChannel.site_id == site_dict['id']) \
                .filter(LiveTVChannel.url == item['url']).one_or_none()
            if not channel:
                channel = LiveTVChannel(url=item['url'], site_id=site_dict['id'])
                spider.logger.debug('新增频道 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新频道 {}:{}'.format(item['name'], item['url']))
            channel.from_item(item)
            self.session.add(channel)
            self.session.commit()
            if not channel.office_id:
                channel.office_id = channel.id
                self.session.add(channel)
                self.session.commit()
            if channel.short not in site_dict['channels']:
                site_dict['channels'][channel.short] = {'id': channel.id, 'total': 0}
        elif isinstance(item, RoomItem):
            room = self.session.query(LiveTVRoom) \
                .filter(LiveTVRoom.site_id == site_dict['id']) \
                .filter(LiveTVRoom.office_id == item['office_id']).one_or_none()
            if not room:
                room = LiveTVRoom(office_id=item['office_id'], site_id=site_dict['id'])
                spider.logger.debug('新增房间 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新房间 {}:{}'.format(item['name'], item['url']))
            channel_dict = site_dict['channels'].get(item['channel'], {})
            if 'id' in channel_dict:
                room.channel_id = channel_dict['id']
                channel_dict['total'] += 1
            room.from_item(item)
            self.session.add(room)
            self.session.commit()
            self.session.add(LiveTVRoomPresent(room_id=room.id, online=room.online))
            self.session.commit()
        return item


class StatisticPipeline(object):

    def __init__(self, sqlalchemy_database_uri):
        self.engine = create_engine(sqlalchemy_database_uri)
        self.session_maker = sessionmaker(bind=self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlalchemy_database_uri=crawler.settings.get('SQLALCHEMY_DATABASE_URI')
        )

    def open_spider(self, spider):
        self.session = self.session_maker()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        if isinstance(item, DailyItem):
            daily = LiveTVRoomDaily(site_id=item['site_id'], room_id=item['room_id'],
                                    summary_date=item['summary_date'], online=item['online'],
                                    followers=item['followers'], description=item['description'],
                                    announcement=item['announcement'])
            self.session.add(daily)
            self.session.commit()
            if item['fallback']:
                room = self.session.query(LiveTVRoom).filter_by(id=item['room_id']).one_or_none()
                if room:
                    room.followers = item['followers']
                    room.description = item['description']
                    room.announcement = item['announcement']
                    self.session.add(room)
                    self.session.commit()
            self.session.query(LiveTVRoomPresent).filter_by(crawl_date_format=item['summary_date']).delete()
            self.session.commit()
        return item
