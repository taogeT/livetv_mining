# -*- coding: UTF-8 -*-
from ... import db
from . import LiveTVChannel, LiveTVRoom, LiveTVChannelData, LiveTVRoomData

__all__ = ['DouyuChannel', 'DouyuRoom', 'DouyuChannelData', 'DouyuRoomData']


class DouyuChannel(LiveTVChannel):
    """ 频道 """
    __tablename__ = 'douyu_channel'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'), primary_key=True)

    tags = db.Column(db.PickleType, doc='标签')

    __mapper_args__ = {
        'polymorphic_identity': 'douyu',
    }


class DouyuRoom(LiveTVRoom):
    """ 房间 """
    __tablename__ = 'douyu_room'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True)

    weight = db.Column(db.String(32), doc='体重')
    weight_int = db.Column(db.Integer, index=True, doc='体重数值')
    start_time = db.Column(db.DateTime, index=True, doc='开播时间')
    owner_avatar = db.Column(db.String(1024), doc='播主头像地址')
    owner_uid = db.Column(db.String(32), doc='播主uid')

    __mapper_args__ = {
        'polymorphic_identity': 'douyu',
    }


class DouyuChannelData(LiveTVChannelData):
    """ 扫描频道数据保存，作为曲线图基础数据 """
    __tablename__ = 'douyu_channel_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel_data.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'douyu',
    }


class DouyuRoomData(LiveTVRoomData):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'douyu_room_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room_data.id'), primary_key=True)

    weight = db.Column(db.String(32), doc='体重')
    weight_int = db.Column(db.Integer, index=True, doc='体重数值')

    __mapper_args__ = {
        'polymorphic_identity': 'douyu',
    }


class DouyuGift(db.Model):
    """ 斗鱼所有礼物类型 """
    __tablename__ = 'douyu_gift'
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
