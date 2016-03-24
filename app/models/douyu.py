# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, \
                                       StaleElementReferenceException
from datetime import datetime

from .. import db
from . import LiveTVSite, LiveTVChannel, LiveTVRoom, get_webdirver_client

import requests
import json


class DouyuTVChannel(db.Model, LiveTVChannel):
    __tablename__ = 'douyutvchannel'

    rooms = db.relationship('DouyuTVRoom', backref='channel', lazy='dynamic')

    @classmethod
    def scan_channel(cls, site_url):
        site = LiveTVSite.query.filter_by(scan_url=site_url).one()
        ''' 扫描频道, 目前需要弹出firefox浏览器，需改进 '''
        current_app.logger.info('调用目录接口:{}'.format(site.scan_url))
        resp = requests.get(site.scan_url)
        if resp.status_code != 200:
            current_app.logger.error('调用接口失败，status_code: {}, content: {}'.format(resp.status_code, resp.content))
            return
        respjson = resp.json()
        if respjson['error'] != 0:
            current_app.logger.error('调用接口失败:{}'.format(respjson['data']))
            return
        for channel_json in respjson['data']:
            channel = cls.query.filter_by(url=channel_json['game_url']).one_or_none()
            if not channel:
                channel = cls(url=channel_json['game_url'])
                current_app.logger.info('新增频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
            else:
                current_app.logger.info('更新频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
            channel.site_id = site.id
            channel.officeid = channel_json['cate_id']
            channel.name = channel_json['game_name']
            channel.short_name = channel_json['short_name']
            channel.image_url = channel_json['game_src']
            channel.icon_url = channel_json['game_icon']
            db.session.add(channel)
        db.session.commit()


class DouyuTVRoom(db.Model, LiveTVRoom):
    __tablename__ = 'douyutvroom'
    ROOM_API = 'http://api.douyutv.com/api/v1/live'

    channel_id = db.Column(db.Integer, db.ForeignKey('douyutvchannel.id'))

    @classmethod
    def scan_room(cls, site_scan_url=None, channel_url=None):
        if not site_scan_url and not channel_url:
            raise ValueError('At Lease input one param: site_url/channel_url')
        elif channel_url:
            channel = DouyuTVChannel.query.filter_by(url=channel_url).one()
            site = LiveTVSite.query.get(channel.site_id)
            return cls._scan_room_inner(channel, site.url)
        elif site_scan_url:
            site = LiveTVSite.query.filter_by(scan_url=site_scan_url).one()
            channels = [channel for channel in DouyuTVChannel.query.filter_by(site_id=site.id)]
            while len(channels) > 0:
                channel = channels.pop(0)
                if not cls._scan_room_inner(channel, site.url):
                    channels.append(channel)
            return True

    @classmethod
    def _scan_room_inner(cls, channel, site_url):
        ''' 扫描房间 '''
        channel_api_url = cls.ROOM_API + '/' + channel.officeid
        current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel_api_url))
        scan_offset, scan_limit = 0, 30
        scan_room_count = 0
        webdirver_client = get_webdirver_client()
        while True:
            webdirver_client.get('{}?offset={}&limit={}'.format(channel_api_url, str(scan_offset), str(scan_limit)))
            try:
                pre_element = webdirver_client.find_element_by_tag_name('pre')
            except NoSuchElementException:
                current_app.logger.error('调用接口失败: 内容获取失败')
                return False
            respjson = json.loads(pre_element.get_attribute('innerHTML'))
            if respjson['error'] != 0:
                current_app.logger.error('调用接口失败:{}'.format(respjson['data']))
                return False
            for room_json in respjson['data']:
                room_json['url'] = site_url + room_json['url']
                room = cls.query.filter_by(url=room_json['url']).one_or_none()
                if not room:
                    room = cls(url=room_json['url'])
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                else:
                    current_app.logger.info('更新房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                room.channel = channel
                room.name = room_json['room_name']
                room.boardcaster = room_json['nickname']
                room.popularity = room_json['online']
                room.officeid = room_json['room_id']
                room.follower = room_json['fans']
                room.last_scan_date = datetime.utcnow()
                db.session.add(room)
            scan_room_count += len(respjson['data'])
            if len(respjson['data']) < scan_limit:
                break
            else:
                scan_offset += scan_limit
        channel.range = scan_room_count - channel.roomcount
        channel.roomcount = scan_room_count
        channel.last_scan_date = datetime.utcnow()
        db.session.add(channel)
        db.session.commit()
        return True
