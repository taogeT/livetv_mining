# -*- coding: UTF-8 -*-
from datetime import datetime

from . import db


class LiveTVSite(db.Model):
    __tablename__ = 'livetv_site'
    ''' 直播网站 '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True, doc='名称')
    displayname = db.Column(db.String(128), index=True, doc='显示名称')
    url = db.Column(db.String(1024), unique=True, index=True, doc='官网地址')
    crawl_url = db.Column(db.String(256), doc='扫描链接')
    image_url = db.Column(db.String(1024), doc='图片')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增时间')
    last_crawl_date = db.Column(db.DateTime, index=True, doc='最近一次扫描时间')
    order_int = db.Column(db.Integer, index=True, doc='排序')
    description = db.Column(db.String(1024), doc='描述')
    valid = db.Column(db.Boolean, default=True, doc='有效')

    channels = db.relationship('LiveTVChannel', backref='site', lazy='dynamic')


class LiveTVChannel(db.Model):
    __tablename__ = 'livetv_channel'
    ''' 频道 '''
    id = db.Column(db.Integer, primary_key=True)
    officeid = db.Column(db.String(128), index=True, doc='官方ID')
    name = db.Column(db.String(128), index=True, doc='名称')
    short_name = db.Column(db.String(128), index=True, doc='简称')
    url = db.Column(db.String(1024), unique=True, index=True, doc='官网地址')
    image_url = db.Column(db.String(1024), doc='图片')
    icon_url = db.Column(db.String(1024), doc='图标')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增时间')
    last_crawl_date = db.Column(db.DateTime, index=True, doc='最近一次扫描时间')
    range = db.Column(db.Integer, index=True, default=0, doc='房间增减幅度')
    roomcount = db.Column(db.Integer, index=True, default=0, doc='活动房间总数')

    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    rooms = db.relationship('LiveTVRoom', backref='channel', lazy='dynamic')
    dataset = db.relationship('LiveTVChannelData', backref='channel', lazy='dynamic')


class LiveTVRoom(db.Model):
    __tablename__ = 'livetv_room'
    ''' 房间 '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, doc='名称')
    url = db.Column(db.String(512), unique=True, index=True, doc='访问URL')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增日期')
    popularity = db.Column(db.Integer, index=True, doc='人气/观众')
    reward = db.Column(db.Integer, index=True, doc='酬劳')
    boardcaster = db.Column(db.String(128), doc='主播名')
    last_active = db.Column(db.Boolean, index=True, default=False, doc='最近一次扫描有参与')
    last_crawl_date = db.Column(db.DateTime, index=True, doc='最近一次扫描时间')
    officeid = db.Column(db.String(128), index=True, doc='官方ID')
    follower = db.Column(db.Integer, index=True, doc='关注')
    image_url = db.Column(db.String(1024), doc='图片')

    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))
    dataset = db.relationship('LiveTVRoomData', backref='room', lazy='dynamic')


class LiveTVChannelData(db.Model):
    __tablename__ = 'livetv_channel_data'
    ''' 扫描频道数据保存，作为曲线图基础数据 '''
    id = db.Column(db.Integer, primary_key=True)
    roomcount = db.Column(db.Integer, default=0, doc='活动房间总数')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增日期')

    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))


class LiveTVRoomData(db.Model):
    __tablename__ = 'livetv_room_data'
    ''' 扫描房间数据保存，作为曲线图基础数据 '''
    id = db.Column(db.Integer, primary_key=True)
    popularity = db.Column(db.Integer, index=True, doc='人气')
    reward = db.Column(db.Integer, index=True, doc='酬劳')
    follower = db.Column(db.Integer, index=True, doc='关注')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增日期')

    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'))
