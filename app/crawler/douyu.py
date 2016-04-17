# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime

from .. import db
from . import LiveTVCrawler, LiveTVSite, LiveTVChannel, LiveTVRoom, \
              LiveTVChannelData, LiveTVRoomData

import requests

CHANNEL_API = 'http://open.douyucdn.cn/api/RoomApi/game'
ROOM_LIST_API = 'http://open.douyucdn.cn/api/RoomApi/live/{}?offset={}&limit={}'
ROOM_API = 'http://open.douyucdn.cn/api/RoomApi/room/{}'

req_headers = {
    'Host': 'open.douyucdn.cn',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
}


class DouyuCrawler(LiveTVCrawler):

    def _get_site(self):
        site = LiveTVSite.query.filter_by(name='douyu').one_or_none()
        if not site:
            site = LiveTVSite(name='douyu', url='http://www.douyu.com',
                              displayname='斗鱼', valid='true', rder_int=1,
                              image_url='http://staticlive.douyutv.com/common/douyu/images/logo_zb.png',
                              description='斗鱼-全民直播平台')
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
        if respjson['error'] != 0:
            current_app.logger.error('调用接口失败: 返回错误结果{}'.format(respjson))
            return False
        site.channels.update({'valid': False})
        for channel_json in respjson['data']:
            channel = site.channels.filter_by(officeid=channel_json['cate_id']).one_or_none()
            if not channel:
                channel = LiveTVChannel(officeid=channel_json['cate_id'])
                current_app.logger.info('新增频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
            else:
                current_app.logger.info('更新频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
            channel.site = site
            channel.url = channel_json['game_url']
            channel.name = channel_json['game_name']
            channel.short_name = channel_json['short_name']
            channel.image_url = channel_json['game_src']
            channel.icon_url = channel_json['game_icon']
            channel.valid = True
            db.session.add(channel)
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道房间 {}: {}'.format(channel.name, channel.url))
        channel.rooms.update({'last_active': False})
        crawl_offset, crawl_limit = 0, 100
        crawl_room_count = 0
        while True:
            requrl = ROOM_LIST_API.format(channel.officeid, crawl_offset, crawl_limit)
            resp = requests.get(requrl, headers=req_headers)
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(requrl))
                return False
            if respjson['error'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果{}'.format(requrl, respjson))
                return False
            for room_json in respjson['data']:
                room = channel.rooms.filter_by(officeid=room_json['room_id']).one_or_none()
                if not room:
                    room = LiveTVRoom(officeid=room_json['room_id'])
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                else:
                    current_app.logger.info('更新房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
                room.channel = channel
                room.url = room_json['url']
                room.name = room_json['room_name']
                room.boardcaster = room_json['nickname']
                room.popularity = room_json['online']
                room.last_active = True
                room.last_crawl_date = datetime.utcnow()
                room_data = LiveTVRoomData(room=room, popularity=room.popularity)
                db.session.add(room, room_data)
            crawl_room_count += len(respjson['data'])
            if len(respjson['data']) < crawl_limit:
                break
            else:
                crawl_offset += crawl_limit
        channel.range = crawl_room_count - channel.roomcount
        channel.roomcount = crawl_room_count
        channel.last_crawl_date = datetime.utcnow()
        channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
        db.session.add(channel, channel_data)
        db.session.commit()
        return True

    def _single_room(self, room):
        room_requrl = ROOM_API.format(room.officeid)
        room_resp = requests.get(room_requrl, headers=req_headers)
        try:
            room_respjson = room_resp.json()
        except ValueError:
            current_app.logger.error('调用房间接口{}失败: 内容解析json失败'.format(room_requrl))
            return False
        if room_respjson['error'] != 0:
            current_app.logger.error('调用房间接口{}失败: 返回错误结果{}'.format(room_requrl, room_respjson))
            return False
        room.name = room_respjson['data']['room_name']
        room.boardcaster = room_respjson['data']['owner_name']
        room.popularity = room_respjson['data']['online']
        room.follower = room_respjson['data']['fans_num']
        owner_weight = room_respjson['data']['owner_weight']
        if owner_weight.endswith('t'):
            room.reward = int(float(owner_weight[:-1]) * 1000 * 1000)
        elif owner_weight.endswith('kg'):
            room.reward = int(float(owner_weight[:-2]) * 1000)
        elif owner_weight.endswith('g'):
            room.reward = int(owner_weight[:-1])
        room.last_active = True
        room.last_crawl_date = datetime.utcnow()
        room_data = LiveTVRoomData(room=room, popularity=room.popularity,
                                   follower=room.follower, reward=room.reward)
        db.session.add(room, room_data)
        return True
