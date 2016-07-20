# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime
from lxml import etree, html
from urllib.parse import urljoin
from requests.exceptions import ConnectionError, ProxyError

from gevent.queue import Empty as GeventEmpty

from ... import db
from ...models.bilibili import *
from .. import base_headers

import gevent

__all__ = ['settings', 'crawl_task', 'request_headers',
           'crawl_channel_list', 'crawl_room_list', 'search_room_list', 'crawl_room_all', 'crawl_room']

CHANNEL_LIST_API = 'http://live.bilibili.com'
ROOM_LIST_API = 'http://live.bilibili.com/area/liveList'
ROOM_API = 'http://live.bilibili.com/live/getInfo'
SPACE_API = 'http://space.bilibili.com'
request_headers = dict(base_headers, Host='live.bilibili.com', Referer='live.bilibili.com')
settings = {
    'code': 'bilibili',
    'name': '哔哩哔哩',
    'description': '哔哩哔哩-关注ACG直播互动平台',
    'url': 'http://live.bilibili.com',
    'image_url': 'http://static.hdslb.com/live-static/common/images/logo/logo-150-cyan.png',
    'order_int': 4,
}


def crawl_task(self):
    self.crawl_channel_list()
    self.crawl_room_list(self.site.channels.filter_by(valid=True).all())


def crawl_channel_list(self):
    current_app.logger.info('调用频道接口:{}'.format(CHANNEL_LIST_API))
    respcontent = self._get_response(CHANNEL_LIST_API, to_json=False)
    self.site.channels.update({'valid': False})
    htmlroot = etree.HTML(respcontent)
    for channel_element in htmlroot.xpath('//div[contains(@class, "main-section") and contains(@class, "no-hidden") and contains(@class, "clear-float")]'):
        channel_element = html.document_fromstring(html.tostring(channel_element))
        link_element = channel_element.xpath('//a[@class="section-more-link"]')[0]
        channel_code = link_element.get('href')[1:]
        channel_name = channel_element.xpath('//div[contains(@class, "section-title")]')[0].get('title')
        channel = BilibiliChannel.query.filter_by(code=channel_code).one_or_none()
        if not channel:
            channel = BilibiliChannel(code=channel_code, site=self.site)
            current_app.logger.info('新增频道 {}'.format(channel_name))
        else:
            current_app.logger.info('更新频道 {}'.format(channel_name))
        channel.url = urljoin(self.site.url, link_element.get('href'))
        channel.name = channel_name
        channel.valid = True
        channel.tags = [tag_element.text for tag_element in channel_element.xpath('//div[@class="live-tag"]')]
        db.session.add(channel)
    self.site.crawl_date = datetime.utcnow()
    db.session.add(self.site)
    db.session.commit()


def crawl_room_list(self, channel_list):
    for channel in channel_list:
        channel.rooms.update({'openstatus': False})
        db.session.commit()
    gpool, gqueue = self._gevent_pool_search(channel_list, self.search_room_list)
    while gpool.free_count() < gpool.size or not gqueue.empty():
        try:
            restype, channel, resjson = gqueue.get(timeout=0.1)
        except GeventEmpty:
            continue
        if restype == 'room_list':
            for room_json in resjson:
                host = BilibiliHost.query.filter_by(officeid=str(room_json['uid'])).one_or_none()
                if not host:
                    host = BilibiliHost(officeid=str(room_json['uid']), site=self.site)
                    current_app.logger.info('新增主持 {}:{}'.format(room_json['uid'], room_json['uname']))
                else:
                    current_app.logger.debug('更新主持 {}:{}'.format(room_json['uid'], room_json['uname']))
                host.nickname = room_json['uname']
                host.url = urljoin(SPACE_API, str(room_json['uid']))
                host.image_url = room_json['face']
                host.master_level = room_json['master_level']
                host.followers = room_json['attentions']
                host.crawl_date = datetime.utcnow()
                db.session.add(host)

                room = BilibiliRoom.query.filter_by(officeid=str(room_json['roomid'])).one_or_none()
                if not room:
                    room = BilibiliRoom(officeid=str(room_json['roomid']), site=self.site)
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['roomid'], room_json['title']))
                else:
                    current_app.logger.debug('更新房间 {}:{}'.format(room_json['roomid'], room_json['title']))
                room.channel = channel
                room.host = host
                room.name = room_json['title']
                room.image_url = room_json['cover']
                room.online = room_json['online']
                room.crawl_date = datetime.utcnow()
                room.openstatus = True
                room.short_id = room_json['short_id']
                room.live_time = datetime.strptime(room_json['live_time'], '%Y-%m-%d %H:%M:%S')
                room.url = urljoin(self.site.url, room_json['link'])
                db.session.add(room)
                room_data = BilibiliRoomData(room=room, online=room.online)
                db.session.add(room_data)
                channel.officeid = room_json['area']
        elif restype == 'channel':
            db.session.add(channel)
            db.session.add(resjson)
        db.session.commit()


def search_room_list(self, channel, gqueue):
    current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
    crawl_page, crawl_limit = 1, 32
    crawl_room_count, roomjsonlen = 0, crawl_limit
    while roomjsonlen >= crawl_limit:
        roomjsonlen = 0
        for i in range(3):
            params = {'order': 'online', 'area': channel.code, 'page': crawl_page}
            try:
                respjson = self._get_response(ROOM_LIST_API, params=params)
            except (ConnectionError, ProxyError, ValueError):
                continue
            if respjson['code'] != 0:
                current_app.logger.error('调用接口 {} {} 失败: 返回错误结果{}'.format(ROOM_LIST_API, channel.code, respjson))
                continue
            roomjsonlen = len(respjson['data'])
            gqueue.put(('room_list', channel, respjson['data']))
            break
        else:
            error_msg = '扫描频道房间超过次数失败 {}: {}'.format(channel.name, channel.url)
            current_app.logger.error(error_msg)
            gqueue.put(('error', channel, error_msg))
        crawl_room_count += roomjsonlen
        crawl_page += 1
        gevent.sleep(self._interval_seconds())
    channel.room_range = crawl_room_count - channel.room_total
    channel.room_total = crawl_room_count
    channel.crawl_date = datetime.utcnow()
    channel_data = BilibiliChannelData(channel=channel, room_total=channel.room_total)
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
    current_app.logger.info('开始扫描房间详细信息: {} {}'.format(ROOM_API, room.officeid))
    params = {'roomid': room.officeid}
    respjson = self._get_response(ROOM_API, params=params)
    if respjson['code'] != 0:
        error_msg = '调用房间接口 {} {} 失败: 返回错误结果{}'.format(ROOM_API, room.officeid, respjson)
        current_app.logger.error(error_msg)
        gqueue.put(('error', (room, error_msg)))
    room_respjson = respjson['data']
    room.name = room_respjson['ROOMTITLE']
    room.image_url = room_respjson['COVER']
    room.openstatus = room_respjson['LIVE_STATUS'] == 'LIVE'
    room.score = room_respjson['RCOST']
    room.crawl_date = datetime.utcnow()
    room_data = BilibiliRoomData(room=room, online=room.online, score=room.score)
    gqueue.put(('room', (room, room_data)))
    room.host.nickname = room_respjson['ANCHOR_NICK_NAME']
    room.host.followers = room_respjson['FANS_COUNT']
    room.host.url = urljoin(SPACE_API, room.host.officeid)
    room.host.crawl_date = datetime.utcnow()
    host_data = BilibiliHostData(host=room.host, followers=room.host.followers)
    gqueue.put(('host', (room.host, host_data)))
    current_app.logger.info('结束扫描房间详细信息: {} {}'.format(ROOM_API, room.officeid))
    gevent.sleep(self._interval_seconds())
