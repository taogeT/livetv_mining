# -*- coding: UTF-8 -*-
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LiveTVSite(Base):
    """ 直播站点 """
    __tablename__ = 'livetv_site'

    id = Column(Integer, primary_key=True)
    channels = relationship('LiveTVChannel', backref='site', lazy='dynamic')
    rooms = relationship('LiveTVRoom', backref='site', lazy='dynamic')

    code = Column(String(32), unique=True, index=True, doc='代码')
    name = Column(String(64), doc='名称')
    url = Column(String(1024), unique=True, index=True, doc='官网地址')
    image = Column(String(1024), doc='图片')
    show_seq = Column(Integer, index=True, doc='排序')
    description = Column(String(512), doc='站点描述')
    valid = Column(Boolean, default=True, doc='是否有效')


class LiveTVChannel(Base):
    """ 频道 """
    __tablename__ = 'livetv_channel'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('livetv_site.id'), index=True)
    rooms = relationship('LiveTVRoom', backref='channel', lazy='dynamic')

    office_id = Column(String(32), index=True, doc='官方ID')
    short = Column(String(64), index=True, doc='简称')
    name = Column(String(128), index=True, doc='名称')
    url = Column(String(1024), unique=True, doc='官网地址')
    image = Column(String, doc='图片')
    total = Column(Integer, default=0, index=True, doc='房间数')
    valid = Column(Boolean, default=True, doc='是否有效')
    crawl_date = Column(DateTime, doc='最近一次扫描时间')

    def from_item(self, item):
        self.office_id = item.get('office_id', self.office_id)
        self.short = item['short']
        self.name = item['name']
        self.url = item['url']
        self.image = item.get('image', self.image)
        self.crawl_date = datetime.utcnow()


class LiveTVRoom(Base):
    """ 房间 """
    __tablename__ = 'livetv_room'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('livetv_channel.id'), index=True)
    site_id = Column(Integer, ForeignKey('livetv_site.id'), index=True)

    office_id = Column(String(32), index=True, doc='官方ID')
    name = Column(String(258), index=True, doc='名称')
    url = Column(String(1024), index=True, doc='访问URL')
    image = Column(String(1024), doc='图片')
    host = Column(String(128), doc='主持')
    online = Column(Integer, default=0, index=True, doc='观众数')
    opened = Column(Boolean, default=True, index=True, doc='是否正在直播')
    crawl_date = Column(DateTime, index=True, doc='最近一次扫描时间')
    followers = Column(Integer, default=0, index=True, doc='关注者数')
    description = Column(TEXT, doc='描述')
    announcement = Column(String(1024), doc='公告')
    start_time = Column(DateTime, index=True, doc='开播时间')

    def from_item(self, item):
        self.office_id = item['office_id']
        self.name = item['name']
        self.url = item['url']
        self.image = item['image']
        self.host = item['host']
        self.online = item['online']
        self.opened = True
        self.crawl_date = datetime.utcnow()
        self.followers = item.get('followers', self.followers)
        self.description = item.get('description', self.description)
        self.announcement = item.get('announcement', self.announcement)
        self.start_time = item.get('start_time', self.start_time)


DAILY_DATE_FORMAT = '%Y%m%d'


class LiveTVRoomPresent(Base):
    """ 房间更新实时信息 """
    __tablename__ = 'livetv_room_present'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('livetv_room.id'), index=True)

    crawl_date = Column(DateTime, default=datetime.utcnow, index=True, doc='扫描时间')
    online = Column(Integer, default=0, index=True, doc='观众数')
    crawl_date_format = Column(String(32), default=lambda: datetime.utcnow().strftime(DAILY_DATE_FORMAT), index=True,
                               doc='扫描时间格式化')


class LiveTVRoomDaily(Base):
    """ 房间每日信息 """
    __tablename__ = 'livetv_room_daily'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('livetv_site.id'), index=True)
    room_id = Column(Integer, ForeignKey('livetv_room.id'), index=True)

    summary_date = Column(String(32), index=True, doc='扫描时间')
    online = Column(Integer, default=0, index=True, doc='观众数')
    followers = Column(Integer, default=0, index=True, doc='关注者数')
    description = Column(TEXT, doc='描述')
    announcement = Column(String(1024), doc='公告')
