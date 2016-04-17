# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .. import db
from . import LiveTVCrawler, LiveTVSite, LiveTVChannel, LiveTVRoom, \
              LiveTVChannelData, LiveTVRoomData, get_webdriver_client

import requests
import json

CHANNEL_API = 'http://api.m.panda.tv/ajax_get_all_subcate'
ROOM_LIST_API = 'http://www.panda.tv/ajax_sort?classification={}&pageno={}&pagenum={}'
ROOM_API = 'http://api.m.panda.tv/ajax_get_liveroom_baseinfo?roomid={}'

req_headers = {
    'Host': 'api.m.panda.tv',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
}


class PandaCrawler(LiveTVCrawler):

    def _get_site(self):
        site = LiveTVSite.query.filter_by(name='panda').one_or_none()
        if not site:
            site = LiveTVSite(name='panda', displayname='熊猫', order_int=2,
                              url='http://www.panda.tv', valid='true',
                              image_url='http://i8.pdim.gs/8f40398337db212845d4884b68cc7e8d.png',
                              description='熊猫TV_最娱乐的直播平台')
            db.session.add(site)
            db.session.commit()
        return site

    def _channels(self, site):
        current_app.logger.info('调用频道接口:{}'.format(CHANNEL_API))
        resp = requests.get(CHANNEL_API, headers=req_headers)
        try:
            respjson = resp.json()
        except ValueError:
            current_app.logger.error('调用接口失败: 内容解析json失败')
            return False
        if respjson['errno'] != 0:
            current_app.logger.error('调用接口失败: 返回错误结果 {}'.format(respjson['errmsg']))
            return False
        site.channels.update({'valid': False})
        for channel_json in respjson['data']:
            channel_json['url'] = '{}/{}'.format(site.url, channel_json['ename'])
            channel = site.channels.filter_by(short_name=channel_json['ename']).one_or_none()
            if not channel:
                channel = LiveTVChannel(short_name=channel_json['ename'])
                current_app.logger.info('新增频道 {}: {}'.format(channel_json['cname'], channel_json['url']))
            else:
                current_app.logger.info('更新频道 {}: {}'.format(channel_json['cname'], channel_json['url']))
            channel.site = site
            channel.name = channel_json['cname']
            channel.url = channel_json['url']
            channel.image_url = channel_json['img']
            channel.icon_url = channel_json['img']
            channel.valid = True
            db.session.add(channel)
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道 {}: {}'.format(channel.name, channel.url))
        channel.rooms.update({'last_active': False})
        crawl_pageno, crawl_pagenum = 1, 120
        crawl_room_count = 0
        webdriver_client = get_webdriver_client()
        try:
            while True:
                try:
                    requrl = ROOM_LIST_API.format(channel.short_name, str(crawl_pageno), str(crawl_pagenum))
                    webdriver_client.get(requrl)
                    body_element = webdriver_client.find_element_by_tag_name('body')
                except (NoSuchElementException, TimeoutException):
                    current_app.logger.error('调用频道接口失败: 内容获取失败')
                    return False
                try:
                    respjson = json.loads(body_element.get_attribute('innerHTML'))
                except ValueError:
                    current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(requrl))
                    return False
                if respjson['errno'] != 0:
                    current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(requrl, respjson['errmsg']))
                    return False
                crawl_room_results = respjson['data']['items']
                for room_json in crawl_room_results:
                    room = channel.rooms.filter_by(officeid=room_json['hostid']).one_or_none()
                    if not room:
                        room = LiveTVRoom(officeid=room_json['hostid'])
                        current_app.logger.info('新增房间 {}:{}'.format(room_json['hostid'], room_json['name']))
                    else:
                        current_app.logger.info('更新房间 {}:{}'.format(room_json['hostid'], room_json['name']))
                    room.channel = channel
                    room.name = room_json['name']
                    room.url = '{}/{}'.format(channel.site.url, room_json['id'])
                    room.boardcaster = room_json['userinfo']['nickName']
                    room.popularity = room_json['person_num']
                    room.last_active = True
                    room.last_crawl_date = datetime.utcnow()
                    room_data = LiveTVRoomData(room=room, popularity=room.popularity)
                    db.session.add(room, room_data)
                crawl_room_count += len(crawl_room_results)
                if len(crawl_room_results) < crawl_pagenum:
                    break
                else:
                    crawl_pageno += 1
            channel.range = crawl_room_count - channel.roomcount
            channel.roomcount = crawl_room_count
            channel.last_crawl_date = datetime.utcnow()
            channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
            db.session.add(channel, channel_data)
            db.session.commit()
            return True
        finally:
            webdriver_client.close()
            webdriver_client.quit()

    def _single_room(self, room):
        room_requrl = ROOM_API.format(room.url[room.url.rfind('/')+1:])
        room_resp = requests.get(room_requrl, headers=req_headers)
        try:
            room_respjson = room_resp.json()
        except ValueError:
            current_app.logger.error('调用房间接口{}失败: 内容解析json失败'.format(room_requrl))
            return False
        if room_respjson['errno'] != 0:
            current_app.logger.error('调用房间接口{}失败: 返回错误结果{}'.format(room_requrl, room_respjson['errmsg']))
            return False
        room_respjson = room_respjson['data']['info']
        room.name = room_respjson['roominfo']['name']
        room.boardcaster = room_respjson['hostinfo']['name']
        room.popularity = room_respjson['roominfo']['person_num']
        room.follower = room_respjson['roominfo']['fans']
        room.reward = int(room_respjson['hostinfo']['bamboos'])
        room.last_active = True
        room.last_crawl_date = datetime.utcnow()
        room_data = LiveTVRoomData(room=room, popularity=room.popularity,
                                   follower=room.follower, reward=room.reward)
        db.session.add(room, room_data)
        return True
