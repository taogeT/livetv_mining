# -*- coding: UTF-8 -*-
from flask import current_app, copy_current_request_context
from datetime import datetime
from urllib.parse import urljoin
from gevent.pool import Pool as GeventPool
from gevent.queue import Queue as GeventQueue, Empty as GeventEmpty

from ... import db
from ..models.zhanqi import *
from .. import base_headers

import requests

__all__ = ['settings', 'crawl_task', 'request_headers',
           'crawl_channel_list', 'crawl_room_list', 'search_room_list', 'crawl_room_all', 'crawl_room']

CHANNEL_LIST_API = 'http://www.zhanqi.tv/api/static/game.lists/300-1.json'
ROOM_LIST_API = 'http://www.zhanqi.tv/api/static/game.lives/{}/{}-{}.json'
ROOM_API = 'http://www.zhanqi.tv/api/static/live.roomid/{}.json'
request_headers = dict(base_headers, Host='www.zhanqi.tv', Referer='http://www.zhanqi.tv')
settings = {
    'code': 'zhanqi',
    'name': '战旗',
    'description': '战旗TV_高清流畅的游戏直播平台',
    'url': 'http://www.zhanqi.tv',
    'image_url': 'http://dlstatic.cdn.zhanqi.tv/assets/web/static/i/new-index-logo2.png',
    'order_int': 3
}


def crawl_task(self):
    self.crawl_channel_list()
    self.crawl_room_list([channel for channel in list(ZhanqiChannel.query.filter_by(valid=True))])


def crawl_channel_list(self):
    current_app.logger.info('调用频道接口:{}'.format(CHANNEL_LIST_API))
    resp = self._get_response(CHANNEL_LIST_API)
    if not resp or resp.status_code != requests.codes.ok:
        error_msg = '调用接口{}失败: 状态{}'.format(CHANNEL_LIST_API, resp.status_code if resp else '')
        current_app.logger.error(error_msg)
        raise ValueError(error_msg)
    respjson = resp.json()
    if respjson['code'] != 0:
        error_msg = '调用接口失败: 返回错误结果{}'.format(respjson)
        current_app.logger.error(error_msg)
        raise ValueError(error_msg)
    self.site.channels.update({'valid': False})
    for channel_json in respjson['data']['games']:
        channel_json['url'] = urljoin(self.site.url, channel_json['url'])
        channel = ZhanqiChannel.query.filter_by(officeid=channel_json['id']).one_or_none()
        if not channel:
            channel = ZhanqiChannel(officeid=channel_json['id'], site=self.site)
            current_app.logger.info('新增频道 {}:{}'.format(channel_json['name'], channel_json['url']))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_json['name'], channel_json['url']))
        channel.url = channel_json['url']
        channel.name = channel_json['name']
        channel.code = channel_json['gameKey']
        channel.image_url = channel_json['spic']
        channel.weight = int(channel_json['weight']) if channel_json['weight'] and channel_json['weight'].isdecimal() else 0
        channel.valid = True
        db.session.add(channel)
    self.site.crawl_date = datetime.utcnow()
    db.session.add(self.site)
    db.session.commit()


def crawl_room_list(self, channel_list):
    gpool = GeventPool(current_app.config['GEVENT_POOL_SIZE'])
    gqueue = GeventQueue()
    for channel in channel_list:
        channel.rooms.update({'openstatus': False})
        db.session.commit()
        gpool.spawn(copy_current_request_context(self.search_room_list), channel, gqueue)
    while not gqueue.empty() or gpool.free_count() < gpool.size:
        try:
            restype, channel, resjson = gqueue.get(timeout=1)
        except GeventEmpty:
            current_app.logger.info('等待队列结果...')
            continue
        if restype == 'room_list':
            for room_json in resjson:
                host = ZhanqiHost.query.filter_by(officeid=str(room_json['uid'])).one_or_none()
                if not host:
                    host = ZhanqiHost(officeid=str(room_json['uid']), site=self.site)
                    current_app.logger.info('新增主持 {}:{}'.format(room_json['uid'], room_json['nickname']))
                else:
                    current_app.logger.debug('更新主持 {}:{}'.format(room_json['uid'], room_json['nickname']))
                host.nickname = room_json['nickname']
                host.image_url = room_json['avatar']
                host.crawl_date = datetime.utcnow()
                db.session.add(host)

                room = ZhanqiRoom.query.filter_by(officeid=room_json['id']).one_or_none()
                if not room:
                    room = ZhanqiRoom(officeid=room_json['id'], site=self.site)
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['id'], room_json['title']))
                else:
                    current_app.logger.debug('更新房间 {}:{}'.format(room_json['id'], room_json['title']))
                room.channel = channel
                room.host = host
                room.name = room_json['title']
                room.url = urljoin(channel.site.url, room_json['url'])
                room.image_url = room_json['bpic']
                room.spectators = int(room_json['online']) if room_json['online'].isdecimal() else 0
                room.crawl_date = datetime.utcnow()
                room.openstatus = True
                room.code = room_json['code']
                room.liveTime = datetime.fromtimestamp(float(room_json['liveTime']))
                db.session.add(room)
                room_data = ZhanqiRoomData(room=room, spectators=room.spectators)
                db.session.add(room_data)
        elif restype == 'channel':
            db.session.add(channel)
            channel_data = ZhanqiChannelData(channel=channel, room_total=channel.room_total)
            db.session.add(channel_data)
        db.session.commit()


def search_room_list(self, channel, gqueue):
    current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
    crawl_pageno, crawl_pagenum = 1, 100
    crawl_room_count, roomjsonlen = 0, crawl_pagenum
    while roomjsonlen >= crawl_pagenum:
        for i in range(3):
            requrl = ROOM_LIST_API.format(channel.officeid, crawl_pagenum, crawl_pageno)
            resp = self._get_response(requrl)
            if not resp or resp.status_code != requests.codes.ok:
                current_app.logger.error('调用接口 {} 失败: 状态{}'.format(requrl, resp.status_code if resp else ''))
                continue
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口 {} 失败: 内容解析json失败'.format(requrl))
                continue
            if respjson['code'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果{}'.format(requrl, respjson))
                continue
            roomjsonlen = len(respjson['data']['rooms'])
            gqueue.put(('room_list', channel, respjson['data']['rooms']))
            break
        else:
            error_msg = '扫描频道房间超过次数失败 {}: {}'.format(channel.name, channel.url)
            current_app.logger.error(error_msg)
            gqueue.put(('error', channel, error_msg))
            raise ValueError(error_msg)
        crawl_room_count += roomjsonlen
        crawl_pageno += 1
    channel.room_range = crawl_room_count - channel.room_total
    channel.room_total = crawl_room_count
    channel.crawl_date = datetime.utcnow()
    gqueue.put(('channel', channel, None))
    current_app.logger.info('结束扫描频道房间 {}: {}'.format(channel.name, channel.url))


def crawl_room_all(self):
    gpool = GeventPool(current_app.config['GEVENT_POOL_SIZE'])
    gqueue = GeventQueue()
    for room in list(ZhanqiRoom.query.filter_by(openstatus=True)):
        gpool.spawn(copy_current_request_context(self.crawl_room), room, gqueue)
    while not gqueue.empty() or gpool.free_count() < gpool.size:
        try:
            current_app.logger.info('等待队列结果...')
            restype, resjson = gqueue.get(timeout=1)
        except GeventEmpty:
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
        db.session.commit()


def crawl_room(self, room, gqueue):
    room_requrl = ROOM_API.format(room.officeid)
    current_app.logger.info('开始扫描房间详细信息: {}'.format(room_requrl))
    room_resp = self._get_response(room_requrl)
    if not room_resp or room_resp.status_code != requests.codes.ok:
        error_msg = '调用接口 {} 失败: 状态{}'.format(room_requrl, room_resp.status_code if room_resp else '')
        current_app.logger.error(error_msg)
        gqueue.put(('error', error_msg))
        raise ValueError(error_msg)
    respjson = room_resp.json()
    if respjson['code'] != 0:
        error_msg = '调用房间接口 {} 失败: 返回错误结果{}'.format(room_requrl, respjson)
        current_app.logger.error(error_msg)
        gqueue.put(('error', error_msg))
        raise ValueError(error_msg)
    room_respjson = respjson['data']
    room.name = room_respjson['title']
    room.image_url = room_respjson['bpic']
    room.spectators = int(room_respjson['online']) if room_respjson['online'].isdecimal() else 0
    room.crawl_date = datetime.utcnow()
    room.code = room_respjson['code']
    room.liveTime = datetime.fromtimestamp(float(room_respjson['liveTime']))
    room.fans = room_respjson['fans']
    room.fansTitle = room_respjson['fansTitle']
    room.isstar_week = room_respjson['isStar']['isWeek'] != 0
    room.isstar_month = room_respjson['isStar']['isMonth'] != 0
    room_data = ZhanqiRoomData(room=room, spectators=room.spectators, fans=room.fans)
    gqueue.put(('room', (room, room_data)))
    room.host.nickname = room_respjson['nickname']
    room.host.image_url = room_respjson['avatar']
    room.host.followers = room_respjson['follows']
    room.host.followers = int(room_respjson['anchorAttr']['hots']['fight']) if room_respjson['anchorAttr']['hots']['fight'].isdecimal() else 0
    room.host.crawl_date = datetime.utcnow()
    host_data = ZhanqiHostData(host=room.host, followers=room.host.followers, fight=room.host.fight)
    gqueue.put(('host', (room.host, host_data)))
    current_app.logger.info('结束扫描房间详细信息: {}'.format(room_requrl))
