# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import CloseSpider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .items import ChannelItem, RoomItem
from .models import LiveTVSite, LiveTVChannel, LiveTVRoom, LiveTVRoomData


class SqlalchemyPipeline(object):

    def __init__(self, sqlalchemy_database_uri):
        self.engine = create_engine(sqlalchemy_database_uri)
        self.site = {}

    def __del__(self):
        self.engine.dispose()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlalchemy_database_uri=crawler.settings.get('SQLALCHEMY_DATABASE_URI'),
        )

    def open_spider(self, spider):
        session = sessionmaker(bind=self.engine)()
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
        self.site[site.code] = {'id': site.id, 'session': session, 'channels': {}}

    def close_spider(self, spider):
        site_dict = self.site[spider.settings.get('SITE')['code']]
        for channel in site_dict['session'].query(LiveTVChannel).filter(LiveTVChannel.site_id == site_dict['id']).all():
            channel.total = channel.rooms.count()
            site_dict['session'].add(channel)
        site_dict['session'].commit()
        site_dict['session'].close()

    def process_item(self, item, spider):
        site_dict = self.site[spider.settings.get('SITE')['code']]
        if isinstance(item, ChannelItem):
            channel = site_dict['session'].query(LiveTVChannel) \
                .filter(LiveTVChannel.site_id == site_dict['id']) \
                .filter(LiveTVChannel.short == item['short']).one_or_none()
            if not channel:
                channel = LiveTVChannel(short=item['short'], site_id=site_dict['id'])
                spider.logger.debug('新增频道 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新频道 {}:{}'.format(item['name'], item['url']))
            channel.from_item(item)
            site_dict['session'].add(channel)
            site_dict['session'].commit()
            if not channel.office_id:
                channel.office_id = channel.id
                site_dict['session'].add(channel)
                site_dict['session'].commit()
            site_dict['channels'][channel.short] = channel.id
        elif isinstance(item, RoomItem):
            room = site_dict['session'].query(LiveTVRoom) \
                .filter(LiveTVRoom.site_id == site_dict['id']) \
                .filter(LiveTVRoom.channel_id == site_dict['channels'][item['channel']]) \
                .filter(LiveTVRoom.office_id == item['office_id']).one_or_none()
            if not room:
                room = LiveTVRoom(office_id=item['office_id'], site_id=site_dict['id'],
                                  channel_id=site_dict['channels'][item['channel']])
                spider.logger.debug('新增房间 {}: {}'.format(item['name'], item['url']))
            else:
                spider.logger.debug('更新房间 {}:{}'.format(item['name'], item['url']))
            room.from_item(item)
            site_dict['session'].add(room)
            site_dict['session'].commit()
        return item
