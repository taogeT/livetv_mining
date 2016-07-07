# -*- coding: UTF-8 -*-
from ... import db
from . import LiveTVChannel, LiveTVRoom, LiveTVHost, \
              LiveTVChannelData, LiveTVRoomData, LiveTVHostData

__all__ = ['PandaChannel', 'PandaRoom', 'PandaHost',
           'PandaChannelData', 'PandaRoomData', 'PandaHostData']


class PandaChannel(LiveTVChannel):
    """ 频道 """
    __tablename__ = 'panda_channel'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'), primary_key=True)

    ext = db.Column(db.String(32), index=True, doc='额外标识')

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


class PandaRoom(LiveTVRoom):
    """ 房间 """
    __tablename__ = 'panda_room'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'), primary_key=True)

    bamboos = db.Column(db.Integer, index=True, doc='竹子数值')
    bulletin = db.Column(db.String(256), doc='公告')
    details = db.Column(db.Text, doc='详细内容')
    qrcode_url = db.Column(db.String(1024), unique=True, doc='二维码URL')
    start_time = db.Column(db.DateTime, index=True, doc='开始时间')
    end_time = db.Column(db.DateTime, index=True, doc='结束时间')
    duration = db.Column(db.Integer, index=True, doc='持续秒数')

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


class PandaHost(LiveTVHost):
    """ 房间 """
    __tablename__ = 'panda_host'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


class PandaChannelData(LiveTVChannelData):
    """ 扫描频道数据保存，作为曲线图基础数据 """
    __tablename__ = 'panda_channel_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_channel_data.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


class PandaRoomData(LiveTVRoomData):
    """ 扫描房间数据保存，作为曲线图基础数据 """
    __tablename__ = 'panda_room_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_room_data.id'), primary_key=True)

    bamboos = db.Column(db.Integer, index=True, doc='竹子数值')

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


class PandaHostData(LiveTVHostData):
    """ 扫描主持数据保存，作为曲线图基础数据 """
    __tablename__ = 'panda_host_data'
    id = db.Column(db.Integer, db.ForeignKey('livetv_host_data.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'panda',
    }


'''
class PandaGift(db.Model):
    """ 斗鱼所有礼物类型 """
    __tablename__ = 'panda_gift'
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
