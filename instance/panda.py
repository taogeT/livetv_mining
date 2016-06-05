# -*- coding: UTF-8 -*-
from flask import current_app
from datetime import datetime
from lxml import etree

from . import db, request_headers, LiveTVCrawler
from . import LiveTVSite, LiveTVChannel, LiveTVRoom, LiveTVChannelData, LiveTVRoomData

import requests

CHANNEL_API = 'http://www.panda.tv/cate'
ROOM_LIST_API = 'http://www.panda.tv/ajax_sort?classification={}&pageno={}&pagenum={}'
ROOM_API = 'http://www.panda.tv/api_room?roomid={}'
panda_headers = dict(request_headers, Host='www.panda.tv', Referer='http://www.panda.tv')


class PandaCrawler(LiveTVCrawler):

    def _get_site(self):
        site = LiveTVSite.query.filter_by(name='panda').one_or_none()
        if not site:
            site = LiveTVSite(name='panda', displayname='熊猫', order_int=2, url='http://www.panda.tv', valid='true',
                              image_url='http://i8.pdim.gs/8f40398337db212845d4884b68cc7e8d.png',
                              description='熊猫TV_最娱乐的直播平台')
            db.session.add(site)
            db.session.commit()
        return site

    def _channels(self, site):
        current_app.logger.info('调用频道接口:{}'.format(CHANNEL_API))
        resp = self._get_response(CHANNEL_API, headers=panda_headers)
        if resp.status_code != requests.codes.ok:
            current_app.logger.error('调用接口{}失败: 状态{}'.format(CHANNEL_API, resp.status_code))
            return False
        site.channels.update({'valid': False})
        db.session.commit()
        htmlroot = etree.HTML(resp.content)
        dirul = htmlroot.xpath('//ul[contains(@class,\'video-list\')]')[0]
        for channel_a_element in dirul.xpath('./li/a'):
            channel_url = channel_a_element.get('href')
            if 'http://' in channel_url or 'https://' in channel_url:
                continue
            img_element = channel_a_element.xpath('./div[@class=\'img-container\']/img')[0]
            channel_img_url = img_element.get('src')
            div_element = channel_a_element.xpath('./div[@class=\'cate-title\']')[0]
            channel_name = div_element.text.strip()
            channel_short_name = channel_url.split('/')[-1]
            channel_url = '{}/{}'.format(site.url, channel_url)
            channel = site.channels.filter_by(short_name=channel_short_name).one_or_none()
            if not channel:
                channel = LiveTVChannel(short_name=channel_short_name)
                current_app.logger.info('新增频道 {}: {}'.format(channel_name, channel_url))
            else:
                current_app.logger.info('更新频道 {}: {}'.format(channel_name, channel_url))
            channel.site = site
            channel.name = channel_name
            channel.url = channel_url
            channel.image_url = channel_img_url
            channel.icon_url = channel_img_url
            channel.valid = True
        db.session.commit()
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True

    def _rooms(self, channel):
        current_app.logger.info('开始扫描频道 {}: {}'.format(channel.name, channel.url))
        channel.rooms.update({'last_active': False})
        db.session.commit()
        crawl_pageno, crawl_pagenum = 1, 120
        crawl_room_count = 0
        while True:
            requrl = ROOM_LIST_API.format(channel.short_name, crawl_pageno, crawl_pagenum)
            resp = self._get_response(requrl, headers=panda_headers)
            if resp.status_code != requests.codes.ok:
                current_app.logger.error('调用接口{}失败: 状态{}'.format(requrl, resp.status_code))
                return False
            try:
                respjson = resp.json()
            except ValueError:
                current_app.logger.error('调用接口{}失败: 内容解析json失败'.format(requrl))
                return False
            if respjson['errno'] != 0:
                current_app.logger.error('调用接口{}失败: 返回错误结果 {}'.format(requrl, respjson['errmsg']))
                return False
            crawl_room_results = respjson['data']['items']
            for room_json in crawl_room_results:
                room = LiveTVRoom.query.join(LiveTVChannel) \
                                 .filter(LiveTVChannel.site_id == channel.site.id) \
                                 .filter(LiveTVRoom.officeid == room_json['id']).one_or_none()
                if not room:
                    room = LiveTVRoom(officeid=room_json['id'])
                    current_app.logger.info('新增房间 {}:{}'.format(room_json['id'], room_json['name']))
                else:
                    current_app.logger.info('更新房间 {}:{}'.format(room_json['id'], room_json['name']))
                room.channel = channel
                room.name = room_json['name']
                room.url = '{}/{}'.format(channel.site.url, room_json['id'])
                room.boardcaster = room_json['userinfo']['nickName']
                room.popularity = room_json['person_num']
                room.last_active = True
                room.last_crawl_date = datetime.utcnow()
                room_data = LiveTVRoomData(room=room, popularity=room.popularity)
                db.session.add(room)
                db.session.add(room_data)
            crawl_room_count += len(crawl_room_results)
            if len(crawl_room_results) < crawl_pagenum:
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
        room_resp = self._get_response(room_requrl, headers=panda_headers)
        if room_resp.status_code != requests.codes.ok:
            current_app.logger.error('调用接口{}失败: 状态{}'.format(room_requrl, room_resp.status_code))
            return False
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
        room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower, reward=room.reward)
        db.session.add(room)
        db.session.add(room_data)
        db.session.commit()
        return True
