# -*- coding: UTF-8 -*-
from flask_login import UserMixin
from datetime import datetime

from . import db


class LiveTVSite(db.Model):
    """ 直播站点 """
    __tablename__ = 'livetv_site'

    id = db.Column(db.Integer, primary_key=True, index=True)
    channels = db.relationship('LiveTVChannel', backref='site', lazy='dynamic')
    rooms = db.relationship('LiveTVRoom', backref='site', lazy='dynamic')

    code = db.Column(db.String(32), unique=True, index=True, doc='代码')
    name = db.Column(db.String(64), doc='名称')
    url = db.Column(db.String(1024), unique=True, index=True, doc='官网地址')
    image = db.Column(db.String(1024), doc='图片')
    show_seq = db.Column(db.Integer, index=True, doc='排序')
    description = db.Column(db.String(512), doc='站点描述')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'url': self.url,
            'image': self.image,
            'description': self.description
        }


class LiveTVChannel(db.Model):
    """ 频道 """
    __tablename__ = 'livetv_channel'

    id = db.Column(db.Integer, primary_key=True, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'), index=True)
    rooms = db.relationship('LiveTVRoom', backref='channel', lazy='dynamic')

    office_id = db.Column(db.String(32), index=True, doc='官方ID')
    short = db.Column(db.String(64), index=True, doc='简称')
    name = db.Column(db.String(128), index=True, doc='名称')
    url = db.Column(db.String(1024), unique=True, doc='官网地址')
    image = db.Column(db.String(1024), doc='图片')
    total = db.Column(db.Integer, default=0, index=True, doc='房间数')
    valid = db.Column(db.Boolean, default=True, doc='是否有效')
    crawl_date = db.Column(db.DateTime, doc='最近一次扫描时间')

    def to_dict(self):
        return {
            'id': self.id,
            'office_id': self.office_id,
            'short': self.short,
            'name': self.name,
            'url': self.url,
            'image': self.image,
            'total': self.total,
            'crawl_date': self.crawl_date.strftime('%Y-%m-%d %H:%M:%S'),
            'site': self.site.name,
            'site_id': self.site_id
        }


class LiveTVRoom(db.Model):
    """ 房间 """
    __tablename__ = 'livetv_room'

    id = db.Column(db.Integer, primary_key=True, index=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'), index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('livetv_site.id'), index=True)

    office_id = db.Column(db.String(32), index=True, doc='官方ID')
    name = db.Column(db.String(258), index=True, doc='名称')
    url = db.Column(db.String(1024), index=True, doc='访问URL')
    image = db.Column(db.String(1024), doc='图片')
    host = db.Column(db.String(128), doc='主持')
    online = db.Column(db.Integer, default=0, index=True, doc='观众数')
    opened = db.Column(db.Boolean, default=True, index=True, doc='是否正在直播')
    crawl_date = db.Column(db.DateTime, index=True, doc='最近一次扫描时间')
    followers = db.Column(db.Integer, default=0, index=True, doc='关注者数')
    description = db.Column(db.TEXT, doc='描述')
    announcement = db.Column(db.String(1024), doc='公告')
    start_time = db.Column(db.DateTime, index=True, doc='开播时间')

    def to_dict(self):
        return {
            'id': self.id,
            'office_id': self.office_id,
            'name': self.name,
            'url': self.url,
            'image': self.image,
            'online': self.online,
            'opened': self.opened,
            'host': self.host,
            'crawl_date': self.crawl_date.strftime('%Y-%m-%d %H:%M:%S'),
            'channel_id': self.channel_id,
            'site_id': self.site_id,
            'channel': self.channel.name,
            'site': self.site.name,
            'followers': self.followers,
            'description': self.description,
            'announcement': self.announcement,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.start_time, datetime) else self.start_time
        }


class LiveTVRoomPresent(db.Model):
    """ 房间更新实时信息 """
    __tablename__ = 'livetv_room_present'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), index=True)

    crawl_date = db.Column(db.DateTime, default=datetime.utcnow, index=True, doc='扫描时间')
    online = db.Column(db.Integer, default=0, index=True, doc='观众数')
    crawl_date_format = db.Column(db.String(32), default=lambda: datetime.utcnow().strftime('%Y%m%d'), index=True,
                                  doc='扫描时间格式化')


class LiveTVRoomDaily(db.Model):
    """ 房间每日信息 """
    __tablename__ = 'livetv_room_daily'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), index=True)

    summary_date = db.Column(db.String(32), index=True, doc='扫描时间')
    online = db.Column(db.Integer, default=0, index=True, doc='观众数')
    followers = db.Column(db.Integer, default=0, index=True, doc='关注者数')
    description = db.Column(db.TEXT, doc='描述')
    announcement = db.Column(db.String(1024), doc='公告')


class User(UserMixin, db.Model):
    """ 用户 """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, index=True)
    rooms = db.relationship('LiveTVRoom', secondary='user_room_link', backref='users', lazy='dynamic')
    symbol = db.Column(db.String(32), doc='站点标记')

    office_id = db.Column(db.String(64), index=True, doc='官方ID')
    username = db.Column(db.String(64), index=True, doc='用户名')
    nickname = db.Column(db.String(128), index=True, doc='显示名称')
    email = db.Column(db.String(256), index=True, doc='邮箱地址')
    url = db.Column(db.Text, doc='空间访问')
    image = db.Column(db.Text, doc='图片')
    description = db.Column(db.Text, doc='描述')
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    subscription = db.Column(db.Integer, index=True, default=3, doc='最大订阅数')

    def to_dict(self):
        return {
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'url': self.url,
            'image': self.image,
            'description': self.description,
            'subscription': self.subscription
        }


class UserRoomLink(db.Model):
    __tablename__ = 'user_room_link'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
