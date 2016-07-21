# -*- coding: UTF-8 -*-
from datetime import datetime

from .. import db


class User(db.Model):
    """ 用户 """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
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
    session_value = db.Column(db.String(1024), index=True, doc='session值')
