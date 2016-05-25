# -*- coding: UTF-8 -*-
from datetime import datetime

from .. import db


class LiveTVChannelData(db.Model):
    __tablename__ = 'livetv_channel_data'
    """ 扫描频道数据保存，作为曲线图基础数据 """
    id = db.Column(db.Integer, primary_key=True)
    roomcount = db.Column(db.Integer, default=0, doc='活动房间总数')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增日期')

    channel_id = db.Column(db.Integer, db.ForeignKey('livetv_channel.id'))


class LiveTVRoomData(db.Model):
    __tablename__ = 'livetv_room_data'
    """ 扫描房间数据保存，作为曲线图基础数据 """
    id = db.Column(db.Integer, primary_key=True)
    popularity = db.Column(db.Integer, index=True, doc='人气')
    reward = db.Column(db.Integer, index=True, doc='酬劳')
    follower = db.Column(db.Integer, index=True, doc='关注')
    since_date = db.Column(db.DateTime, default=datetime.utcnow, doc='新增日期')

    room_id = db.Column(db.Integer, db.ForeignKey('livetv_room.id'))
