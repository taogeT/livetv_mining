# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime
from requests.exceptions import ProxyError, ConnectionError
from gevent.queue import Empty as GeventEmpty

from ... import db
from ..models.douyu import *
from .. import base_headers

import gevent

__all__ = ['settings', 'crawl_task', 'request_headers',
           'crawl_channel_list', 'crawl_room_list', 'search_room_list', 'crawl_room_all', 'crawl_room']

CHANNEL_LIST_API = 'http://www.douyu.com/api/RoomApi/game'
ROOM_LIST_API = 'http://www.douyu.com/api/RoomApi/live/{}'
ROOM_API = 'http://www.douyu.com/api/RoomApi/room/{}'
request_headers = dict(base_headers, Host='www.douyu.com', Referer='http://www.douyu.com')
settings = {
    'code': 'douyu',
    'name': '斗鱼',
    'description': '斗鱼-全民直播平台',
    'url': 'http://www.douyu.com',
    'image_url': 'http://staticlive.douyutv.com/common/douyu/images/logo_zb.png',
    'order_int': 1,
}


def crawl_task(self):
    self.crawl_channel_list()
    self.crawl_room_list(DouyuChannel.query.filter_by(valid=True).all())


def crawl_channel_list(self):
    current_app.logger.info('调用频道接口:{}'.format(CHANNEL_LIST_API))
    respjson = self._get_response(CHANNEL_LIST_API)
    if respjson['error'] != 0:
        error_msg = '调用接口失败: 返回错误结果{}'.format(respjson)
        current_app.logger.error(error_msg)
        raise ValueError(error_msg)
    self.site.channels.update({'valid': False})
    for channel_json in respjson['data']:
        channel = DouyuChannel.query.filter_by(site=self.site, officeid=channel_json['cate_id']).one_or_none()
        if not channel:
            channel = DouyuChannel(officeid=channel_json['cate_id'], site=self.site)
            current_app.logger.info('新增频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
        channel.url = channel_json['game_url']
        channel.name = channel_json['game_name']
        channel.code = channel_json['short_name']
        channel.image_url = channel_json['game_src']
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
            restype, channel_res, resjson = gqueue.get(timeout=0.1)
        except GeventEmpty:
            continue
        if restype == 'room_list':
            for room_json in resjson:
                host = DouyuHost.query.filter_by(officeid=room_json['owner_uid']).one_or_none()
                if not host:
                    host = DouyuHost(officeid=room_json['owner_uid'], site=self.site)
                    current_app.logger.info('新增主持 {}:{}'.format(room_json['owner_uid'], room_json['nickname']))
                else:
                    current_app.logger.debug('更新主持 {}:{}'.format(room_json['owner_uid'], room_json['nickname']))
                host.nickname = room_json['nickname']
                host.image_url = room_json['avatar']
                host.crawl_date = datetime.utcnow()
                db.session.add(host)

                room = DouyuRoom.query.filter_by(officeid=room_json['room_id']).one_or_none()
                if not room:
                    room = DouyuRoom(officeid=room_json['room_id'], site=self.site)
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                else:
                    current_app.logger.debug('更新房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                room.channel = channel_res
                room.host = host
                room.name = room_json['room_name']
                room.image_url = room_json['room_src']
                room.online = room_json['online']
                room.crawl_date = datetime.utcnow()
                room.openstatus = True
                room.url = room_json['url']
                db.session.add(room)
                room_data = DouyuRoomData(room=room, online=room.online)
                db.session.add(room_data)
        elif restype == 'channel':
            db.session.add(channel_res)
            db.session.add(resjson)
        db.session.commit()


def search_room_list(self, channel, gqueue):
    current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
    crawl_offset, crawl_limit = 0, 100
    crawl_room_count = 0
    while True:
        roomjsonlen = 0
        for i in range(3):
            requrl = ROOM_LIST_API.format(channel.officeid)
            params = {'offset': crawl_offset, 'limit': crawl_limit}
            try:
                respjson = self._get_response(requrl, params=params)
            except (ConnectionError, ProxyError, ValueError):
                continue
            if respjson['error'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果{}'.format(requrl, respjson))
                continue
            roomjsonlen = len(respjson['data'])
            gqueue.put(('room_list', channel, respjson['data']))
            break
        else:
            error_msg = '扫描频道房间超过次数失败 {}: {}'.format(channel.name, channel.url)
            current_app.logger.error(error_msg)
            gqueue.put(('error', channel, error_msg))
            raise ValueError(error_msg)
        crawl_room_count += roomjsonlen
        if roomjsonlen < crawl_limit:
            if roomjsonlen + 1 == crawl_limit:
                crawl_offset += crawl_limit - 1
            else:
                break
        else:
            crawl_offset += crawl_limit
        gevent.sleep(self._interval_seconds())
    channel.room_range = crawl_room_count - channel.room_total
    channel.room_total = crawl_room_count
    channel.crawl_date = datetime.utcnow()
    channel_data = DouyuChannelData(channel=channel, room_total=channel.room_total)
    gqueue.put(('channel', channel, channel_data))
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
    room_requrl = ROOM_API.format(room.officeid)
    current_app.logger.info('开始扫描房间详细信息: {}'.format(room_requrl))
    respjson = self._get_response(room_requrl)
    if respjson['error'] != 0:
        error_msg = '调用房间接口{}失败: 返回错误结果{}'.format(room_requrl, respjson)
        current_app.logger.error(error_msg)
        gqueue.put(('error', (room, error_msg)))
        raise ValueError(error_msg)
    room_respjson = respjson['data']
    room.name = room_respjson['room_name']
    room.image_url = room_respjson['room_thumb']
    room.online = room_respjson['online']
    room.openstatus = room_respjson['room_status'] == '1'
    room.weight = room_respjson['owner_weight']
    if room.weight.endswith('t'):
        room.weight_int = int(float(room.weight[:-1]) * 1000 * 1000)
    elif room.weight.endswith('kg'):
        room.weight_int = int(float(room.weight[:-2]) * 1000)
    elif room.weight.endswith('g'):
        room.weight_int = int(room.weight[:-1])
    room.crawl_date = datetime.utcnow()
    room.start_time = datetime.strptime(room_respjson['start_time'], '%Y-%m-%d %H:%M')
    room_data = DouyuRoomData(room=room, online=room.online, weight=room.weight, weight_int=room.weight_int)
    gqueue.put(('room', (room, room_data)))
    room.host.nickname = room_respjson['owner_name']
    room.host.image_url = room_respjson['avatar']
    room.host.followers = int(room_respjson['fans_num']) if room_respjson['fans_num'].isdecimal() else 0
    room.host.crawl_date = datetime.utcnow()
    host_data = DouyuHostData(host=room.host, followers=room.host.followers)
    gqueue.put(('host', (room.host, host_data)))
    current_app.logger.info('结束扫描房间详细信息: {}'.format(room_requrl))
    gevent.sleep(self._interval_seconds())
