# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from scrapy.exceptions import CloseSpider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .items import ChannelItem, RoomItem
from .models import LiveTVSite, LiveTVChannel, LiveTVRoom


class SqlalchemyPipeline(object):

    def __init__(self, sqlalchemy_database_uri):
        self.engine = create_engine(sqlalchemy_database_uri)
        self.session_maker = sessionmaker(bind=self.engine)
        self.site = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlalchemy_database_uri=crawler.settings.get('SQLALCHEMY_DATABASE_URI'),
        )

    def open_spider(self, spider):
        session = self.session_maker()
        site_setting = spider.settings.get('SITE')
        if not site_setting:
            error_msg = 'Can not find the website configuration from settings.'
            spider.logger.error(error_msg)
            raise CloseSpider(error_msg)
        site = session.query(LiveTVSite).filter(LiveTVSite.code == site_setting['code']).one_or_none()
        if not site:
            site = LiveTVSite(code=site_setting['code'], name=site_setting['name'],
                              description=site_setting['description'], url=site_setting['url'],
                              image=site_setting['image'], show_seq=site_setting['show_seq'])
            session.add(site)
            session.commit()
        self.site[site.code] = {'id': site.id, 'starttime': datetime.utcnow(), 'channels': {}}
        session.close()

    def close_spider(self, spider):
        session = self.session_maker()
        site_dict = self.site[spider.settings.get('SITE')['code']]
        session.query(LiveTVRoom).filter(LiveTVRoom.crawl_date < site_dict['starttime']) \
                                 .filter(LiveTVRoom.site_id == site_dict['id']) \
                                 .update({LiveTVRoom.opened: False})
        session.commit()
        for channel in session.query(LiveTVChannel).filter(LiveTVChannel.site_id == site_dict['id']).all():
            channel.total = channel.rooms.filter_by(opened=True).count()
            channel.valid = channel.total > 0
            session.add(channel)
        session.commit()
        session.close()
        del site_dict
        if not self.site:
            self.engine.dispose()

    def process_item(self, item, spider):
        session = self.session_maker()
        site_dict = self.site[spider.settings.get('SITE')['code']]
        if isinstance(item, ChannelItem):
            channel = session.query(LiveTVChannel) \
                .filter(LiveTVChannel.site_id == site_dict['id']) \
                .filter(LiveTVChannel.url == item['url']).one_or_none()
            if not channel:
                channel = LiveTVChannel(url=item['url'], site_id=site_dict['id'])
                spider.logger.debug('新增频道 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新频道 {}:{}'.format(item['name'], item['url']))
            channel.from_item(item)
            session.add(channel)
            session.commit()
            if not channel.office_id:
                channel.office_id = channel.id
                session.add(channel)
                session.commit()
            site_dict['channels'][channel.short] = channel.id
        elif isinstance(item, RoomItem):
            room = session.query(LiveTVRoom) \
                .filter(LiveTVRoom.site_id == site_dict['id']) \
                .filter(LiveTVRoom.office_id == item['office_id']).one_or_none()
            if not room:
                room = LiveTVRoom(office_id=item['office_id'], site_id=site_dict['id'])
                spider.logger.debug('新增房间 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新房间 {}:{}'.format(item['name'], item['url']))
            room.channel_id = site_dict['channels'][item['channel']]
            room.from_item(item)
            session.add(room)
            session.commit()
        session.close()
        return item
