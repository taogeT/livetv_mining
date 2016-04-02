# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

from .. import db
from ..models import LiveTVChannel, LiveTVRoom, LiveTVChannelData, LiveTVRoomData
from . import get_webdirver_client

import json

ROOM_API = 'http://api.douyutv.com/api/v1/live'


def crawl_channel_inner(site):
    current_app.logger.info('调用目录接口:{}'.format(site.crawl_url))
    webdirver_client = get_webdirver_client()
    webdirver_client.get(site.crawl_url)
    try:
        pre_element = webdirver_client.find_element_by_tag_name('pre')
    except NoSuchElementException:
        current_app.logger.error('调用接口失败: 内容获取失败')
        webdirver_client.quit()
        return False
    try:
        respjson = json.loads(pre_element.get_attribute('innerHTML'))
    except ValueError:
        current_app.logger.error('调用接口失败: 内容解析json失败')
        webdirver_client.quit()
        return False
    if respjson['error'] != 0:
        current_app.logger.error('调用接口失败:{}'.format(respjson['data']))
        webdirver_client.quit()
        return False
    for channel_json in respjson['data']:
        channel = LiveTVChannel.query.filter_by(url=channel_json['game_url']).one_or_none()
        if not channel:
            channel = LiveTVChannel(url=channel_json['game_url'])
            current_app.logger.info('新增频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_json['game_name'], channel_json['game_url']))
        channel.site = site
        channel.officeid = channel_json['cate_id']
        channel.name = channel_json['game_name']
        channel.short_name = channel_json['short_name']
        channel.image_url = channel_json['game_src']
        channel.icon_url = channel_json['game_icon']
        db.session.add(channel)
    site.last_crawl_date = datetime.utcnow()
    db.session.add(site)
    db.session.commit()
    webdirver_client.quit()
    return True


def crawl_room_inner(channel):
    channel.rooms.update({'last_active': False})
    channel_api_url = '{}/{}'.format(ROOM_API, channel.officeid)
    current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel_api_url))
    crawl_offset, crawl_limit = 0, 99
    crawl_room_count = 0
    webdirver_client = get_webdirver_client()
    while True:
        try:
            webdirver_client.get('{}?offset={}&limit={}'.format(channel_api_url, str(crawl_offset), str(crawl_limit)))
            pre_element = webdirver_client.find_element_by_tag_name('pre')
        except (NoSuchElementException, TimeoutException):
            current_app.logger.error('调用接口失败: 内容获取失败')
            webdirver_client.quit()
            return False
        try:
            respjson = json.loads(pre_element.get_attribute('innerHTML'))
        except ValueError:
            current_app.logger.error('调用接口失败: 内容解析json失败')
            webdirver_client.quit()
            return False
        if respjson['error'] != 0:
            current_app.logger.error('调用接口失败:{}'.format(respjson['data']))
            webdirver_client.quit()
            return False
        for room_json in respjson['data']:
            room_json['url'] = channel.site.url + room_json['url']
            room = LiveTVRoom.query.filter_by(url=room_json['url']).one_or_none()
            if not room:
                room = LiveTVRoom(url=room_json['url'])
                current_app.logger.info('新增房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
            else:
                current_app.logger.info('更新房间 {}:{}'.format(room_json['room_id'], room_json['room_name']))
            room.channel = channel
            room.name = room_json['room_name']
            room.boardcaster = room_json['nickname']
            room.popularity = room_json['online']
            room.officeid = room_json['room_id']
            room.follower = room_json['fans']
            room.last_active = True
            room.last_crawl_date = datetime.utcnow()
            room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
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
    webdirver_client.quit()
    return True
