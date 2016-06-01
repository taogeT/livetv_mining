# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime

from . import *

import json
import re
import requests
import copy

CHANNEL_API = 'http://www.zhanqi.tv/api/static/game.lists/{}-{}.json'
ROOM_LIST_API = 'http://www.zhanqi.tv/api/static/game.lives/{}/{}-{}.json'
ROOM_API = 'http://www.zhanqi.tv/api/static/live.roomid/{}.json'
zhanqi_headers = copy.deepcopy(request_headers)
zhanqi_headers['Host'] = 'www.zhanqi.tv'


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
        db.session.commit()
        crawl_pageno, crawl_pagenum = 1, 100
        crawl_room_count = 0
        while True:
            requrl = CHANNEL_API.format(crawl_pagenum, crawl_pageno)
            current_app.logger.info('调用频道接口:{}'.format(requrl))
            resp = requests.get(requrl, headers=zhanqi_headers)
            if resp.status_code != requests.codes.ok:
                current_app.logger.error('调用接口{}失败: 状态{}'.format(requrl, resp.status_code))
                return False
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(requrl))
                return False
            if respjson['code'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(requrl, respjson['message']))
                return False
            channel_crawl_results = respjson['data']['games']
            for channel_json in channel_crawl_results:
                if channel_json['url'].startswith('/'):
                    channel_json['url'] = site.url + channel_json['url']
                channel = site.channels.filter_by(officeid=channel_json['id']).one_or_none()
                if not channel:
                    channel = LiveTVChannel(officeid=channel_json['id'])
                    current_app.logger.info('新增频道 {}:{}'.format(channel_json['name'], channel_json['url']))
                else:
                    current_app.logger.info('更新频道 {}:{}'.format(channel_json['name'], channel_json['url']))
                channel.site = site
                channel.name = channel_json['name']
                channel.url = channel_json['url']
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
                db.session.commit()
        db.session.commit()
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
        channel.rooms.update({'last_active': False})
        crawl_pageno, crawl_pagenum = 1, 100
        crawl_room_count = 0
        while True:
            requrl = ROOM_LIST_API.format(channel.officeid, crawl_pagenum, crawl_pageno)
            resp = requests.get(requrl, headers=zhanqi_headers)
            if resp.status_code != requests.codes.ok:
                current_app.logger.error('调用接口{}失败: 状态{}'.format(requrl, resp.status_code))
                return False
            try:
                respjson = re.sub('\"title\":\"[^\"]*\"[^\",]*[\"]+,',
                                  lambda x: '"title":"{}",'.format(x.group(0)[9:-1].replace('"', '')),
                                  resp.text)
                respjson = json.loads(respjson)
            except ValueError:
                current_app.logger.error('获取房间信息解析json.loads失败, {}'.format(respjson))
                return False
            if respjson['code'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(requrl, respjson['message']))
                return False
            room_crawl_results = respjson['data']['rooms']
            for room_crawl_result in room_crawl_results:
                room = LiveTVRoom.query.join(LiveTVChannel) \
                                 .filter(LiveTVChannel.site_id == channel.site.id) \
                                 .filter(LiveTVRoom.officeid == room_crawl_result['id']).one_or_none()
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
                db.session.add(room)
                db.session.add(room_data)
            crawl_room_count += len(room_crawl_results)
            if len(room_crawl_results) < crawl_pagenum:
                break
            else:
                crawl_pageno += 1
                db.session.commit()
        db.session.commit()
        channel.range = crawl_room_count - channel.roomcount
        channel.roomcount = crawl_room_count
        channel.last_crawl_date = datetime.utcnow()
        channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
        db.session.add(channel)
        db.session.add(channel_data)
        db.session.commit()
        return True

    def _single_room(self, room):
        room_requrl = ROOM_API.format(room.officeid)
        room_resp = requests.get(room_requrl, headers=zhanqi_headers)
        if room_resp.status_code != requests.codes.ok:
            current_app.logger.error('调用接口{}失败: 状态{}'.format(room_requrl, room_resp.status_code))
            return False
        try:
            room_respjson = room_resp.json()
        except ValueError:
            current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(room_requrl))
            return False
        if room_respjson['code'] != 0:
            current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(room_requrl, room_respjson['message']))
            return False
        room.name = room_respjson['data']['title']
        room.boardcaster = room_respjson['data']['nickname']
        room.popularity = room_respjson['data']['online']
        room.follower = room_respjson['data']['follows']
        room.last_active = True
        room.last_crawl_date = datetime.utcnow()
        room_data = LiveTVRoomData(room=room, popularity=room.popularity,
                                   follower=room.follower, reward=room.reward)
        db.session.add(room)
        db.session.add(room_data)
        db.session.commit()
        return True
