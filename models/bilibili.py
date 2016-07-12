# -*- coding: UTF-8 -*-
from ... import db
from . import LiveTVChannel, LiveTVRoom, LiveTVHost, \
              LiveTVChannelData, LiveTVRoomData, LiveTVHostData

__all__ = ['BilibiliChannel', 'BilibiliRoom', 'BilibiliHost',
           'BilibiliChannelData', 'BilibiliRoomData', 'BilibiliHostData']


class BilibiliChannel(LiveTVChannel):
    """ 频道 """
    __tablename__ = 'bilibili_channel'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'), primary_key=True)

    tags = db.Column(db.PickleType, doc='标签')

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


class BilibiliRoom(LiveTVRoom):
    """ 房间 """
    __tablename__ = 'bilibili_room'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True)

    tags = db.Column(db.PickleType, doc='标签')
    short_id = db.Column(db.String(32), doc='短ID')
    live_time = db.Column(db.DateTime, index=True, doc='开播时间')
    score = db.Column(db.Integer, index=True, doc='积分')

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


class BilibiliHost(LiveTVHost):
    """ 房间 """
    __tablename__ = 'bilibili_host'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host.id'), primary_key=True)

    master_level = db.Column(db.Integer, default=0, index=True, doc='级别')

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


class BilibiliChannelData(LiveTVChannelData):
    """ 扫描频道数据保存，作为曲线图基础数据 """
    __tablename__ = 'bilibili_channel_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel_data.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


class BilibiliRoomData(LiveTVRoomData):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'bilibili_room_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room_data.id'), primary_key=True)

    score = db.Column(db.Integer, index=True, doc='积分')

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


class BilibiliHostData(LiveTVHostData):
    """ 扫描主持数据保存，作为曲线图基础数据 """
    __tablename__ = 'bilibili_host_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host_data.id'), primary_key=True)

    master_level = db.Column(db.Integer, default=0, index=True, doc='级别')

    __mapper_args__ = {
        'polymorphic_identity': 'bilibili',
    }


'''
class BilibiliGift(db.Model):
    """ 斗鱼所有礼物类型 """
    __tablename__ = 'bilibili_gift'
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(16), index=True, doc='礼物ID')
    name = db.Column(db.String(64), index=True, doc='名称')
    gifttype = db.Column(db.Integer, index=True, doc='类型')
    pc = db.Column(db.Integer, index=True, doc='价格')
    gx = db.Column(db.Integer, index=True, doc='贡献值')
    desc = db.Column(db.String(256), doc='描述')
    intro = db.Column(db.String(256), doc='介绍')
    mimg = db.Column(db.String(1024), doc='图标静态图片地址')
    himg = db.Column(db.String(1024), doc='图标动态图片地址')
'''