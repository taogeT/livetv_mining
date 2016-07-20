# -*- coding: UTF-8 -*-
from datetime import datetime

from .. import db


class LiveTVSite(db.Model):
    """ 直播站点 """
    __tablename__ = 'livetv_site'
    id = db.Column(db.Integer, primary_key=True)
    channels = db.relationship('LiveTVChannel', backref='site', lazy='dynamic')
    rooms = db.relationship('LiveTVRoom', backref='site', lazy='dynamic')
    hosts = db.relationship('LiveTVHost', backref='site', lazy='dynamic')

    code = db.Column(db.String(64), unique=True, index=True, doc='代码')
    name = db.Column(db.String(128), doc='名称')
    url = db.Column(db.String(1024), unique=True, doc='官网地址')
    image_url = db.Column(db.String(1024), doc='图片')
    order_int = db.Column(db.Integer, index=True, doc='排序')
    description = db.Column(db.String(1024), doc='站点描述')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')


class LiveTVChannel(db.Model):
    """ 频道 """
    __tablename__ = 'livetv_channel'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    rooms = db.relationship('LiveTVRoom', backref='channel', lazy='dynamic')
    dataset = db.relationship('LiveTVChannelData', backref='channel', lazy='dynamic')
    symbol = db.Column(db.String(32), doc='站点标记')

    officeid = db.Column(db.String(64), index=True, doc='官方ID')
    code = db.Column(db.String(64), index=True, doc='代码')
    name = db.Column(db.String(256), index=True, doc='名称')
    url = db.Column(db.String(1024), index=True, doc='官网地址')
    image_url = db.Column(db.String(1024), doc='图片')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')
    room_total = db.Column(db.Integer, index=True, default=0, doc='房间总数')
    room_range = db.Column(db.Integer, index=True, default=0, doc='房间增减数')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


class LiveTVRoom(db.Model):
    """ 房间 """
    __tablename__ = 'livetv_room'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('livetv_host.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    dataset = db.relationship('LiveTVRoomData', backref='room', lazy='dynamic')
    symbol = db.Column(db.String(32), doc='站点标记')

    officeid = db.Column(db.String(64), index=True, doc='官方ID')
    name = db.Column(db.String(1024), index=True, doc='名称')
    url = db.Column(db.String(1024), index=True, doc='访问URL')
    image_url = db.Column(db.String(1024), doc='图片')
    online = db.Column(db.Integer, default=0, index=True, doc='观众数')
    openstatus = db.Column(db.Boolean, default=True, doc='是否正在直播')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


class LiveTVHost(db.Model):
    """ 房间 """
    __tablename__ = 'livetv_host'
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    rooms = db.relationship('LiveTVRoom', backref='host', lazy='dynamic')
    dataset = db.relationship('LiveTVHostData', backref='host', lazy='dynamic')
    symbol = db.Column(db.String(32), doc='站点标记')

    officeid = db.Column(db.String(64), index=True, doc='官方ID')
    username = db.Column(db.String(64), index=True, doc='用户名')
    nickname = db.Column(db.String(256), index=True, doc='显示名称')
    url = db.Column(db.String(1024), doc='空间访问')
    image_url = db.Column(db.String(1024), doc='图片')
    followers = db.Column(db.Integer, default=0, index=True, doc='关注数')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


class LiveTVChannelData(db.Model):
    """ 扫描频道数据保存，作为曲线图基础数据 """
    __tablename__ = 'livetv_channel_data'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))
    symbol = db.Column(db.String(32), doc='站点标记')

    create_date = db.Column(db.DateTime, default=datetime.now, index=True, doc='创建时间')
    room_total = db.Column(db.Integer, default=0, index=True, doc='活动房间总数')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


class LiveTVRoomData(db.Model):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'livetv_room_data'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'))
    symbol = db.Column(db.String(32), doc='站点标记')

    create_date = db.Column(db.DateTime, default=datetime.now, index=True, doc='创建时间')
    online = db.Column(db.Integer, default=0, doc='观众数')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


class LiveTVHostData(db.Model):
    """ 扫描主持人数据保存，作为曲线图基础数据 """
    __tablename__ = 'livetv_host_data'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('livetv_host.id'))
    symbol = db.Column(db.String(32), doc='站点标记')

    create_date = db.Column(db.DateTime, default=datetime.now, index=True, doc='创建时间')
    followers = db.Column(db.Integer, default=0, index=True, doc='关注数')

    __mapper_args__ = {
        'polymorphic_identity': 'livetv',
        'polymorphic_on': symbol,
        'with_polymorphic': '*'
    }


from .douyu import *
from .panda import *
from .zhanqi import *
from .bilibili import *
