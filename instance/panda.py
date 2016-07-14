# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime
from urllib.parse import urljoin
from gevent.queue import Empty as GeventEmpty
from requests.exceptions import ConnectionError, ProxyError

from ... import db
from ..models.panda import *
from .. import base_headers

import gevent

__all__ = ['settings', 'crawl_task', 'request_headers',
           'crawl_channel_list', 'crawl_room_list', 'search_room_list', 'crawl_room_all', 'crawl_room']

CHANNEL_LIST_API = 'http://api.m.panda.tv/ajax_get_all_subcate'
ROOM_LIST_API = 'http://www.panda.tv/ajax_sort'
ROOM_API = 'http://www.panda.tv/api_room'
request_headers = dict(base_headers, Host='www.panda.tv', Referer='http://www.panda.tv')
settings = {
    'code': 'panda',
    'name': '熊猫',
    'description': '熊猫TV_最娱乐的直播平台',
    'url': 'http://www.panda.tv',
    'image_url': 'http://i8.pdim.gs/8f40398337db212845d4884b68cc7e8d.png',
    'order_int': 2
}


def crawl_task(self):
    self.crawl_channel_list()
    self.crawl_room_list(self.site.channels.filter_by(valid=True).all())


def crawl_channel_list(self):
    current_app.logger.info('调用频道接口:{}'.format(CHANNEL_LIST_API))
    mobile_headers = dict(self.request_headers, Host='api.m.panda.tv', Referer='http://api.m.panda.tv', xiaozhangdepandatv=1)
    respjson = self._get_response(CHANNEL_LIST_API, headers=mobile_headers)
    if respjson['errno'] != 0:
        error_msg = '调用接口失败: 返回错误结果{}'.format(respjson)
        current_app.logger.error(error_msg)
        raise ValueError(error_msg)
    self.site.channels.update({'valid': False})
    for channel_json in respjson['data']:
        channel_json['url'] = urljoin(self.site.url, 'cate/{}'.format(channel_json['ename']))
        channel = PandaChannel.query.filter_by(code=channel_json['ename']).one_or_none()
        if not channel:
            channel = PandaChannel(code=channel_json['ename'], site=self.site)
            current_app.logger.info('新增频道 {}:{}'.format(channel_json['cname'], channel_json['url']))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_json['cname'], channel_json['url']))
        channel.name = channel_json['cname']
        channel.url = channel_json['url']
        channel.image_url = channel_json['img']
        channel.ext = channel_json['ext']
        channel.valid = True
        db.session.add(channel)
    self.site.crawl_date = datetime.utcnow()
    db.session.add(self.site)
    db.session.commit()


def crawl_room_list(self, channel_list):
    for channel in channel_list:
        channel.rooms.update({'openstatus': False})
        db.session.commit()
    gpool, gqueue = self._gevent_pool_search(channel_list, self.search_room_list)
    while not gqueue.empty() or gpool.free_count() < gpool.size:
        try:
            restype, channel, resjson = gqueue.get(timeout=0.1)
        except GeventEmpty:
            continue
        if restype == 'room_list':
            for room_json in resjson:
                host_json = room_json['userinfo']
                host = PandaHost.query.filter_by(officeid=str(host_json['rid'])).one_or_none()
                if not host:
                    host = PandaHost(officeid=str(host_json['rid']), site=self.site)
                    current_app.logger.info('新增主持 {}:{}'.format(host_json['rid'], host_json['nickName']))
                else:
                    current_app.logger.debug('更新主持 {}:{}'.format(host_json['rid'], host_json['nickName']))
                host.username = host_json['userName']
                host.nickname = host_json['nickName']
                host.image_url = host_json['avatar']
                host.crawl_date = datetime.utcnow()
                db.session.add(host)
                db.session.commit()

                room = PandaRoom.query.filter_by(officeid=room_json['id']).one_or_none()
                if not room:
                    room = PandaRoom(officeid=room_json['id'], site=self.site)
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['id'], room_json['name']))
                else:
                    current_app.logger.debug('更新房间 {}:{}'.format(room_json['id'], room_json['name']))
                room.channel = channel
                room.host = host
                room.name = room_json['name']
                room.url = urljoin(channel.site.url, room_json['id'])
                room.image_url = room_json['pictures']['img']
                room.online = int(room_json['person_num'])
                room.crawl_date = datetime.utcnow()
                room.start_time = datetime.fromtimestamp(float(room_json['start_time']))
                room.end_time = datetime.fromtimestamp(float(room_json['end_time']))
                room.openstatus = True
                room.duration = int(room_json['duration']) if room_json['duration'].isdecimal() else 0
                db.session.add(room)
                room_data = PandaRoomData(room=room, online=room.online)
                db.session.add(room_data)
        elif restype == 'channel':
            db.session.add(channel)
            channel_data = PandaChannelData(channel=channel, room_total=channel.room_total)
            db.session.add(channel_data)
        db.session.commit()


def search_room_list(self, channel, gqueue):
    current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
    crawl_pageno, crawl_pagenum = 1, 120
    crawl_room_count = 0
    while True:
        roomjsonlen = 0
        for i in range(3):
            params = {'classification': channel.code, 'pageno': crawl_pageno, 'pagenum': crawl_pagenum}
            try:
                respjson = self._get_response(ROOM_LIST_API, params=params)
            except (ConnectionError, ProxyError, ValueError):
                continue
            if respjson['errno'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果{}'.format(ROOM_LIST_API, respjson))
                continue
            roomjsonlen = len(respjson['data']['items'])
            gqueue.put(('room_list', channel, respjson['data']['items']))
            break
        else:
            error_msg = '扫描频道房间超过次数失败 {}: {}'.format(channel.name, channel.url)
            current_app.logger.error(error_msg)
            gqueue.put(('error', channel, error_msg))
            raise ValueError(error_msg)
        crawl_room_count += roomjsonlen
        if roomjsonlen < crawl_pagenum:
            if roomjsonlen + 1 == crawl_pagenum:
                crawl_pageno += 1
            else:
                break
        else:
            crawl_pageno += 1
        gevent.sleep(self._interval_seconds())
    channel.room_range = crawl_room_count - channel.room_total
    channel.room_total = crawl_room_count
    channel.crawl_date = datetime.utcnow()
    gqueue.put(('channel', channel, None))
    current_app.logger.info('结束扫描频道房间 {}: {}'.format(channel.name, channel.url))


def crawl_room_all(self):
    room_list = self.site.rooms.filter_by(openstatus=True).all()
    gpool, gqueue = self._gevent_pool_search(room_list, self.crawl_room)
    while not gqueue.empty() or gpool.free_count() < gpool.size:
        try:
            restype, resjson = gqueue.get(timeout=0.1)
        except GeventEmpty:
            gevent.sleep(2)
            continue
        if restype == 'room':
            room, room_data = resjson
            current_app.logger.info('更新房间详细信息 {}:{}'.format(room.officeid, room.name))
            db.session.add(room)
            db.session.add(room_data)
        elif restype == 'host':
            host, host_data = resjson
            current_app.logger.info('更新主持详细信息 {}:{}'.format(host.officeid, host.nickname))
            db.session.add(host)
            db.session.add(host_data)
        elif restype == 'error':
            room, errormsg = resjson
            room.openstatus = False
            db.session.add(room)
        db.session.commit()


def crawl_room(self, room, gqueue):
    params = {'roomid': room.officeid}
    current_app.logger.info('开始扫描房间详细信息: {} {}'.format(ROOM_API, room.officeid))
    respjson = self._get_response(ROOM_API, params=params)
    if respjson['errno'] != 0:
        error_msg = '调用房间接口 {} {} 失败: 返回错误结果{}'.format(ROOM_API, room.officeid, respjson)
        current_app.logger.error(error_msg)
        gqueue.put(('error', (room, error_msg)))
        raise ValueError(error_msg)
    room_respjson = respjson['data']['roominfo']
    host_respjson = respjson['data']['hostinfo']
    room.name = room_respjson['name']
    room.image_url = room_respjson['pictures']['img']
    room.qrcode_url = room_respjson['pictures']['qrcode']
    room.online = int(room_respjson['person_num'])
    room.crawl_date = datetime.utcnow()
    room.start_time = datetime.fromtimestamp(float(room_respjson['start_time']))
    room.end_time = datetime.fromtimestamp(float(room_respjson['end_time']))
    room.openstatus = room.start_time > room.end_time
    if room.openstatus:
        room.duration = int(room_respjson['end_time']) - int(room_respjson['start_time'])
    room.bamboos = int(host_respjson['bamboos'])
    room.bulletin = room_respjson['bulletin']
    room.details = room_respjson['details']
    room_data = PandaRoomData(room=room, online=room.online, bamboos=room.bamboos)
    gqueue.put(('room', (room, room_data)))
    room.host.nickname = host_respjson['name']
    room.host.image_url = host_respjson['avatar']
    room.host.followers = int(room_respjson['fans']) if room_respjson['fans'].isdecimal() else 0
    room.host.crawl_date = datetime.utcnow()
    host_data = PandaHostData(host=room.host, followers=room.host.followers)
    gqueue.put(('host', (room.host, host_data)))
    current_app.logger.info('结束扫描房间详细信息: {} {}'.format(ROOM_API, room.officeid))
    gevent.sleep(self._interval_seconds())
