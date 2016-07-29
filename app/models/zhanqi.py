# -*- coding: UTF-8 -*-
from .. import db
from . import LiveTVChannel, LiveTVRoom, LiveTVHost, \
              LiveTVChannelData, LiveTVRoomData, LiveTVHostData

__all__ = ['ZhanqiChannel', 'ZhanqiRoom', 'ZhanqiHost',
           'ZhanqiChannelData', 'ZhanqiRoomData', 'ZhanqiHostData']


class ZhanqiChannel(LiveTVChannel):
    """ 频道 """
    __tablename__ = 'zhanqi_channel'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'), primary_key=True)

    weight = db.Column(db.Integer, doc='权重')

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


class ZhanqiRoom(LiveTVRoom):
    """ 房间 """
    __tablename__ = 'zhanqi_room'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True)

    fans = db.Column(db.Integer, index=True, doc='粉丝')
    fansTitle = db.Column(db.String(32), doc='粉丝名称')
    isstar_week = db.Column(db.Boolean, default=False, doc='周星')
    isstar_month = db.Column(db.Boolean, default=False, doc='月星')

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


class ZhanqiHost(LiveTVHost):
    """ 房间 """
    __tablename__ = 'zhanqi_host'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host.id'), primary_key=True)

    fight = db.Column(db.Integer, default=0, index=True, doc='战斗力')
    level = db.Column(db.Integer, default=0, index=True, doc='级别')

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


class ZhanqiChannelData(LiveTVChannelData):
    """ 扫描频道数据保存，作为曲线图基础数据 """
    __tablename__ = 'zhanqi_channel_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel_data.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


class ZhanqiRoomData(LiveTVRoomData):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'zhanqi_room_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room_data.id'), primary_key=True)

    fans = db.Column(db.Integer, index=True, doc='粉丝数')

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


class ZhanqiHostData(LiveTVHostData):
    """ 扫描主持数据保存，作为曲线图基础数据 """
    __tablename__ = 'zhanqi_host_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host_data.id'), primary_key=True)

    fight = db.Column(db.Integer, default=0, index=True, doc='战斗力')
    level = db.Column(db.Integer, default=0, index=True, doc='级别')

    __mapper_args__ = {
        'polymorphic_identity': 'zhanqi',
    }


'''
class ZhanqiGift(db.Model):
    """ 斗鱼所有礼物类型 """
    __tablename__ = 'zhanqi_gift'
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
