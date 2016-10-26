# -*- coding: UTF-8 -*-
from flask_login import UserMixin
from datetime import datetime

from . import db


class LiveTVSite(db.Model):
    """ 直播站点 """
    __tablename__ = 'livetv_site'

    id = db.Column(db.Integer, primary_key=True)
    channels = db.relationship('LiveTVChannel', backref='site', lazy='dynamic')
    rooms = db.relationship('LiveTVRoom', backref='site', lazy='dynamic')

    code = db.Column(db.String(32), unique=True, index=True, doc='代码')
    name = db.Column(db.String(64), doc='名称')
    url = db.Column(db.String(1024), unique=True, index=True, doc='官网地址')
    image = db.Column(db.String(1024), doc='图片')
    show_seq = db.Column(db.Integer, index=True, doc='排序')
    description = db.Column(db.String(512), doc='站点描述')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')


class LiveTVChannel(db.Model):
    """ 频道 """
    __tablename__ = 'livetv_channel'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    rooms = db.relationship('LiveTVRoom', backref='channel', lazy='dynamic')

    office_id = db.Column(db.String(32), index=True, doc='官方ID')
    short = db.Column(db.String(64), index=True, doc='简称')
    name = db.Column(db.String(128), index=True, doc='名称')
    url = db.Column(db.String(1024), unique=True, doc='官网地址')
    image = db.Column(db.String(1024), doc='图片')
    total = db.Column(db.Integer, default=0, index=True, doc='房间数')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')


class LiveTVRoom(db.Model):
    """ 房间 """
    __tablename__ = 'livetv_room'

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'))
    hisdata = db.relationship('LiveTVRoomData', backref='room', lazy='dynamic')

    office_id = db.Column(db.String(32), index=True, doc='官方ID')
    name = db.Column(db.String(258), index=True, doc='名称')
    url = db.Column(db.String(1024), index=True, doc='访问URL')
    image = db.Column(db.String(1024), doc='图片')
    host = db.Column(db.String(128), doc='主持')
    online = db.Column(db.Integer, default=0, index=True, doc='观众数')
    opened = db.Column(db.Boolean, default=True, doc='是否正在直播')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')


class LiveTVRoomData(db.Model):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'livetv_room_data'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'))

    create_date = db.Column(db.DateTime, default=datetime.utcnow, index=True, doc='创建时间')
    online = db.Column(db.Integer, default=0, doc='观众数')


class User(UserMixin, db.Model):
    """ 用户 """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    rooms = db.relationship('LiveTVRoom', secondary='user_room_link', backref='users', lazy='dynamic')
    symbol = db.Column(db.String(32), doc='站点标记')

    officeid = db.Column(db.String(64), index=True, doc='官方ID')
    username = db.Column(db.String(64), index=True, doc='用户名')
    nickname = db.Column(db.String(128), index=True, doc='显示名称')
    email = db.Column(db.String(256), index=True, doc='邮箱地址')
    url = db.Column(db.Text, doc='空间访问')
    image_url = db.Column(db.Text, doc='图片')
    description = db.Column(db.Text, doc='描述')
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    subscribe_max = db.Column(db.Integer, index=True, default=1, doc='最大订阅数')


class UserRoomLink(db.Model):
    __tablename__ = 'user_room_link'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
