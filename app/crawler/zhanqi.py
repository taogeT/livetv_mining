# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.common.exceptions import TimeoutException
from datetime import datetime

from .. import db
from . import LiveTVCrawler, LiveTVSite, LiveTVChannel, LiveTVRoom, \
              LiveTVChannelData, LiveTVRoomData, get_webdriver_client

import json
import re

CHANNEL_API = 'http://www.zhanqi.tv/api/static/game.lists/{}-{}.json'
ROOM_LIST_API = 'http://www.zhanqi.tv/api/static/game.lives/{}/{}-{}.json'
ROOM_API = 'http://www.zhanqi.tv/api/static/live.roomid/{}.json'


class ZhanqiCrawler(LiveTVCrawler):

    def _get_site(self):
        site = LiveTVSite.query.filter_by(name='zhanqi').one_or_none()
        if not site:
            site = LiveTVSite(name='zhanqi', displayname='战旗', valid='true',
                              url='http://www.zhanqi.tv', order_int=3,
                              image_url='http://dlstatic.cdn.zhanqi.tv/assets/web/static/i/new-index-logo2.png',
                              description='战旗TV_高清流畅的游戏直播平台')
            db.session.add(site)
            db.session.commit()
        return site

    def _channels(self, site):
        site.channels.update({'valid': False})
        webdriver_client = get_webdriver_client()
        try:
            crawl_pageno, crawl_pagenum = 1, 100
            crawl_room_count = 0
            while True:
                requrl = CHANNEL_API.format(crawl_pagenum, crawl_pageno)
                current_app.logger.info('调用频道接口:{}'.format(requrl))
                try:
                    webdriver_client.get(requrl)
                    body_element = webdriver_client.find_element_by_tag_name('body')
                except TimeoutException:
                    current_app.logger.error('调用接口失败: 内容获取失败')
                    return False
                try:
                    respjson = json.loads(body_element.get_attribute('innerHTML'))
                except ValueError:
                    current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(requrl))
                    return False
                if respjson['code'] != 0:
                    current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(requrl, respjson['message']))
                    return False
                channel_crawl_results = respjson['data']['games']
                for channel_json in channel_crawl_results:
                    if not channel_json['url'].startswith('/'):
                        channel_json['url'] = site.url + channel_json['url']
                    channel = site.channels.filter_by(officeid=channel_json['id']).one_or_none()
                    if not channel:
                        channel = LiveTVChannel(officeid=channel_json['id'])
                        current_app.logger.info('新增频道 {}:{}'.format(channel_json['name'], channel_json['url']))
                    else:
                        current_app.logger.info('更新频道 {}:{}'.format(channel_json['name'], channel_json['url']))
                    channel.site = site
                    channel.name = channel_json['name']
                    channel.short_name = channel_json['gameKey']
                    channel.image_url = channel_json['spic']
                    channel.icon_url = channel_json['icon']
                    channel.valid = True
                    db.session.add(channel)
                crawl_room_count += len(channel_crawl_results)
                if len(channel_crawl_results) < crawl_pagenum:
                    break
                else:
                    crawl_pageno += 1
            site.last_crawl_date = datetime.utcnow()
            db.session.add(site)
            db.session.commit()
            return True
        finally:
            webdriver_client.close()
            webdriver_client.quit()

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
        channel.rooms.update({'last_active': False})
        crawl_pageno, crawl_pagenum = 1, 100
        crawl_room_count = 0
        webdriver_client = get_webdriver_client()
        try:
            while True:
                requrl = ROOM_LIST_API.format(channel.officeid, crawl_pagenum, crawl_pageno)
                webdriver_client.get(requrl)
                room_live_json = webdriver_client.find_element_by_tag_name('body').get_attribute('innerHTML')
                if '系统错误' in room_live_json:
                    current_app.logger.error('获取房间信息失败，重试')
                    return False
                try:
                    room_live_json = re.sub('\"title\":\"[^\"]*\"[^(\",)]*\",\"gameId\"',
                                            lambda x: '"title":"{}","gameId"'.format(x.group(0)[9:-9].replace('"', '')),
                                            room_live_json)
                    room_live_json = json.loads(room_live_json)
                except ValueError:
                    current_app.logger.error('获取房间信息解析json.loads失败, {}'.format(room_live_json))
                    return False
                room_crawl_results = room_live_json['data']['rooms']
                for room_crawl_result in room_crawl_results:
                    room = channel.rooms.filter_by(officeid=room_crawl_result['id']).one_or_none()
                    if not room:
                        room = LiveTVRoom(officeid=room_crawl_result['id'])
                        current_app.logger.info('新增房间 {}:{}'.format(room_crawl_result['id'], room_crawl_result['title']))
                    else:
                        current_app.logger.info('更新房间 {}:{}'.format(room_crawl_result['id'], room_crawl_result['title']))
                    room.channel = channel
                    room.name = room_crawl_result['title']
                    room.url = channel.site.url + room_crawl_result['url']
                    room.boardcaster = room_crawl_result['nickname']
                    room.popularity = int(room_crawl_result['online'])
                    if isinstance(room_crawl_result['follows'], bool) or not isinstance(room_crawl_result['follows'], int):
                        room.follower = 0
                    else:
                        room.follower = room_crawl_result['follows']
                    room.last_active = True
                    room.last_crawl_date = datetime.utcnow()
                    room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
                    db.session.add(room, room_data)
                crawl_room_count += len(room_crawl_results)
                if len(room_crawl_results) < crawl_pagenum:
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
        webdriver_client = get_webdriver_client()
        try:
            room_requrl = ROOM_API.format(room.officeid)
            try:
                webdriver_client.get(room_requrl)
                body_element = webdriver_client.find_element_by_tag_name('body')
            except TimeoutException:
                current_app.logger.error('调用接口失败: 内容获取失败')
                return False
            try:
                room_respjson = json.loads(body_element.get_attribute('innerHTML'))
            except ValueError:
                current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(room_requrl))
                return False
            if room_respjson['code'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(room_requrl, respjson['message']))
                return False
            room.name = room_respjson['data']['title']
            room.boardcaster = room_respjson['data']['nickname']
            room.popularity = room_respjson['data']['online']
            room.follower = room_respjson['data']['follows']
            room.last_active = True
            room.last_crawl_date = datetime.utcnow()
            room_data = LiveTVRoomData(room=room, popularity=room.popularity,
                                       follower=room.follower, reward=room.reward)
            db.session.add(room, room_data)
            return True
        finally:
            webdriver_client.close()
            webdriver_client.quit()
