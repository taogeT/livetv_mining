# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.command import Command
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

from .. import db
from ..models import LiveTVChannel, LiveTVRoom, LiveTVChannelData, LiveTVRoomData
from . import get_webdriver_client

import json

ROOM_LIST_API = 'http://www.panda.tv/ajax_sort?pageno={}&pagenum={}&classification='
ROOM_API = 'http://www.panda.tv/api_room?roomid={}'


def crawl_channel_inner(site):
    webdriver_client = get_webdriver_client()
    try:
        webdriver_client.get(site.crawl_url)
    except (NoSuchElementException, TimeoutException):
        current_app.logger.error('调用接口失败: 内容获取失败')
        webdriver_client.quit()
        return False
    current_app.logger.info('扫描主目录:{}'.format(site.crawl_url))
    try:
        dirul = WebDriverWait(webdriver_client, 30).until(lambda x: x.find_element_by_xpath('//ul[contains(@class,\'video-list\')]'))
    except TimeoutException:
        current_app.logger.error('调用接口失败: 等待读取频道内容失败')
        webdriver_client.quit()
        return False
    for channel_a_element in dirul.find_elements_by_xpath('./li/a'):
        img_element = channel_a_element.find_element_by_xpath('./div[@class=\'img-container\']/img')
        div_element = channel_a_element.find_element_by_xpath('./div[@class=\'cate-title\']')
        channel_name = div_element.get_attribute('innerHTML')
        channel_url = channel_a_element.get_attribute('href')
        channel = LiveTVChannel.query.filter_by(url=channel_url).one_or_none()
        if not channel:
            channel = LiveTVChannel(url=channel_url)
            current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_name, channel_url))
        channel.site = site
        channel.name = channel_name
        channel.short_name = channel_url[channel_url.rfind('/')+1:]
        channel.image_url = img_element.get_attribute('src')
        channel.icon_url = img_element.get_attribute('src')
        db.session.add(channel)
    site.last_crawl_date = datetime.utcnow()
    db.session.add(site)
    db.session.commit()
    webdriver_client.quit()
    return True


def crawl_room_inner(channel):
    channel.rooms.update({'last_active': False})
    channel_api_url = '{}{}'.format(ROOM_LIST_API, channel.short_name)
    current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel_api_url))
    crawl_pageno, crawl_pagenum = 1, 120
    crawl_room_count = 0
    webdriver_client = get_webdriver_client()
    while True:
        try:
            webdriver_client.get(channel_api_url.format(str(crawl_pageno), str(crawl_pagenum)))
            body_element = webdriver_client.find_element_by_tag_name('body')
        except (NoSuchElementException, TimeoutException):
            current_app.logger.error('调用频道接口失败: 内容获取失败')
            webdriver_client.quit()
            return False
        try:
            respjson = json.loads(body_element.get_attribute('innerHTML'))
        except ValueError:
            current_app.logger.error('调用频道接口失败: 内容解析json失败')
            webdriver_client.quit()
            return False
        if respjson['errno'] != 0:
            current_app.logger.error('调用频道接口失败:{}'.format(respjson['data']))
            webdriver_client.quit()
            return False
        for room_json in respjson['data']['items']:
            room = LiveTVRoom.query.filter_by(officeid=room_json['hostid']).one_or_none()
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
            room_api_url = ROOM_API.format(room_json['id'])
            try:
                webdriver_client.get(room_api_url)
            except TimeoutException:
                current_app.logger.error('调用房间接口失败: 内容获取失败')
                webdriver_client.quit()
                return False
            page_source = webdriver_client.page_source
            topindex = page_source.find("\"fans\":\"") + len("\"fans\":\"")
            tailindex = page_source.find("\"", topindex)
            room.follower = int(page_source[topindex:tailindex])
            room.last_active = True
            room.last_crawl_date = datetime.utcnow()
            room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
            db.session.add(room, room_data)
        crawl_room_count += len(respjson['data']['items'])
        if len(respjson['data']['items']) < crawl_pagenum:
            break
        else:
            crawl_pageno += 1
    channel.range = crawl_room_count - channel.roomcount
    channel.roomcount = crawl_room_count
    channel.last_crawl_date = datetime.utcnow()
    channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
    db.session.add(channel, channel_data)
    db.session.commit()
    webdriver_client.quit()
    return True
