# -*- coding: UTF-8 -*-
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LiveTVSite(Base):
    """ 直播站点 """
    __tablename__ = 'livetv_site'

    id = Column(Integer, primary_key=True)
    channels = relationship('LiveTVChannel', backref='site', lazy='dynamic')
    rooms = relationship('LiveTVRoom', backref='site', lazy='dynamic')

    code = Column(String, unique=True, index=True, doc='代码')
    name = Column(String, doc='名称')
    url = Column(String, unique=True, index=True, doc='官网地址')
    image = Column(String, doc='图片')
    show_seq = Column(Integer, index=True, doc='排序')
    description = Column(String, doc='站点描述')
    valid = Column(Boolean, default=True, doc='是否有效')


class LiveTVChannel(Base):
    """ 频道 """
    __tablename__ = 'livetv_channel'

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey('livetv_site.id'))
    rooms = relationship('LiveTVRoom', backref='channel', lazy='dynamic')

    office_id = Column(String, index=True, doc='官方ID')
    short = Column(String, index=True, doc='简称')
    name = Column(String, index=True, doc='名称')
    url = Column(String, index=True, unique=True, doc='官网地址')
    image = Column(String, doc='图片')
    total = Column(Integer, default=0, index=True, doc='房间数')
    crawl_date = Column(DateTime, doc='最近一次扫描时间')

    def from_item(self, item):
        self.office_id = item.get('office_id', '')
        self.short = item['short']
        self.name = item['name']
        self.url = item['url']
        self.image = item.get('image', '')
        self.crawl_date = datetime.utcnow()


class LiveTVRoom(Base):
    """ 房间 """
    __tablename__ = 'livetv_room'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('livetv_channel.id'))
    site_id = Column(Integer, ForeignKey('livetv_site.id'))
    hisdata = relationship('LiveTVRoomData', backref='room', lazy='dynamic')

    office_id = Column(String, index=True, doc='官方ID')
    name = Column(String, index=True, doc='名称')
    url = Column(String, index=True, doc='访问URL')
    image = Column(String, doc='图片')
    online = Column(Integer, default=0, index=True, doc='观众数')
    crawl_date = Column(DateTime, doc='最近一次扫描时间')

    def from_item(self, item):
        self.office_id = item['office_id']
        self.name = item['name']
        self.url = item['url']
        self.image = item['image']
        self.online = item['online']
        self.crawl_date = datetime.utcnow()


class LiveTVRoomData(Base):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'livetv_room_data'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('livetv_room.id'))

    create_date = Column(DateTime, default=datetime.utcnow, index=True, doc='创建时间')
    online = Column(Integer, default=0, doc='观众数')
