# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime

from . import *

import requests

CHANNEL_API = 'https://api.twitch.tv/kraken/games/top'
ROOM_LIST_API = 'https://api.twitch.tv/kraken/search/channels'
ROOM_API = 'https://api.twitch.tv/kraken/channels/{}'

req_headers = {
    'Accept': 'application/vnd.twitchtv.v3+json'
}


class TwitchCrawler(LiveTVCrawler):

    def _get_site(self):
        site = LiveTVSite.query.filter_by(name='twitch').one_or_none()
        if not site:
            site = LiveTVSite(name='twitch', displayname='Twitch', valid='true',
                              url='http://www.twitch.tv', order_int=4,
                              image_url='https://avatars3.githubusercontent.com/u/51763?v=3&s=90',
                              description='Twitch: World\'s leading video platform and community')
            db.session.add(site)
            db.session.commit()
        return site

    def _channels(self, site):
        current_app.logger.info('调用频道接口:{}'.format(CHANNEL_API))
        site.channels.update({'valid': False})
        crawl_params = {'offset': 0, 'limit': 100}
        crawl_room_count = 0
        while True:
            resp = requests.get(CHANNEL_API, params=crawl_params, headers=req_headers)
            if resp.status_code == 503:
                current_app.logger.error('调用接口失败: RESTAPI未启动')
                return False
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口失败: 内容解析json失败')
                return False
            channel_crawl_results = respjson['top']
            for channel_json in channel_crawl_results:
                channel_json = channel_json['game']
                channel = site.channels.filter_by(officeid=str(channel_json['_id'])).one_or_none()
                if not channel:
                    channel = LiveTVChannel(officeid=str(channel_json['_id']))
                    current_app.logger.info('新增频道 {}'.format(channel_json['name']))
                else:
                    current_app.logger.info('更新频道 {}'.format(channel_json['name']))
                channel.site = site
                channel.name = channel_json['name']
                channel.url = '{}/directory/game/{}'.format(site.url, channel_json['name'])
                channel.image_url = channel_json['box']['medium']
                channel.icon_url = channel_json['logo']['medium']
                channel.valid = True
                db.session.add(channel)
            crawl_room_count += len(channel_crawl_results)
            if len(channel_crawl_results) < crawl_params['limit']:
                break
            else:
                crawl_room_count += crawl_params['limit']
                crawl_params['offset'] += crawl_params['limit']
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道 {}: {}'.format(channel.name, ROOM_LIST_API))
        channel.rooms.update({'last_active': False})
        crawl_params = {'offset': 0, 'limit': 100, 'query': channel.name}
        crawl_room_count = 0
        while True:
            resp = requests.get(ROOM_LIST_API, params=crawl_params, headers=req_headers)
            if resp.status_code == 503:
                current_app.logger.error('调用接口失败: RESTAPI未启动')
                return False
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口失败: 内容解析json失败')
                return False
            room_crawl_results = respjson['channels']
            for room_crawl_result in room_crawl_results:
                room = channel.rooms.filter_by(officeid=str(room_crawl_result['_id'])).one_or_none()
                if not room:
                    room = LiveTVRoom(officeid=str(room_crawl_result['_id']))
                    current_app.logger.info('新增房间 {}:{}'.format(room_crawl_result['_id'], room_crawl_result['status']))
                else:
                    current_app.logger.info('更新房间 {}:{}'.format(room_crawl_result['_id'], room_crawl_result['status']))
                room.channel = channel
                room.name = room_crawl_result['status']
                room.boardcaster = room_crawl_result['name']
                room.url = room_crawl_result['url']
                room.popularity = room_crawl_result['views'] if room_crawl_result['views'] else 0
                room.follower = room_crawl_result['followers']
                room.image_url = room_crawl_result['logo']
                room.last_active = True
                room.last_crawl_date = datetime.utcnow()
                room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
                db.session.add(room, room_data)
            crawl_room_count += len(room_crawl_results)
            if len(room_crawl_results) < crawl_params['limit']:
                break
            else:
                crawl_room_count += crawl_params['limit']
                crawl_params['offset'] += crawl_params['limit']
        channel.range = crawl_room_count - channel.roomcount
        channel.roomcount = crawl_room_count
        channel.last_crawl_date = datetime.utcnow()
        channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
        db.session.add(channel, channel_data)
        db.session.commit()
        return True

    def _single_room(self, room):
        room_requrl = ROOM_API.format(room.boardcaster)
        current_app.logger.info('开始扫描房间 {}: {}'.format(room.name, room_requrl))
        room_resp = requests.get(ROOM_LIST_API, headers=req_headers)
        if room_resp.status_code == 503:
            current_app.logger.error('调用接口失败: RESTAPI未启动')
            return False
        try:
            room_respjson = room_resp.json()
        except ValueError:
            current_app.logger.error('调用接口失败: 内容解析json失败')
            return False
        room.url = room_respjson['url']
        room.name = room_respjson['status']
        room.popularity = room_respjson['views']
        room.follower = room_respjson['followers']
        room.image_url = room_respjson['logo']
        room.last_active = True
        room.last_crawl_date = datetime.utcnow()
        room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
        db.session.add(room, room_data)
        db.session.commit()
        return True
