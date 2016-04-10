# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

from .. import db
from ..models import LiveTVChannel, LiveTVRoom, LiveTVChannelData, LiveTVRoomData
from . import get_webdriver_client

import json


def crawl_channel_inner(site):
    webdriver_client = get_webdriver_client()
    try:
        try:
            webdriver_client.get(site.crawl_url)
        except TimeoutException:
            current_app.logger.error('调用接口失败: 内容获取失败')
            return False
        current_app.logger.info('扫描主目录:{}'.format(site.crawl_url))
        try:
            dirul = WebDriverWait(webdriver_client, 30).until(lambda x: x.find_element_by_xpath('//ul[@id=\'game-list-panel\']'))
        except TimeoutException:
            current_app.logger.error('调用接口失败: 等待读取频道内容失败')
            return False
        for channel_a_element in dirul.find_elements_by_xpath('./li/div/a'):
            p_element = channel_a_element.find_element_by_xpath('./p')
            img_element = channel_a_element.find_element_by_xpath('./img')
            channel_name = p_element.get_attribute('innerHTML')
            channel_url = channel_a_element.get_attribute('href')
            channel = LiveTVChannel.query.filter_by(url=channel_url).one_or_none()
            if not channel:
                channel = LiveTVChannel(url=channel_url)
                current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
            else:
                current_app.logger.info('更新频道 {}:{}'.format(channel_name, channel_url))
            channel.site = site
            channel.name = channel_name
            channel.image_url = img_element.get_attribute('src')
            channel.icon_url = img_element.get_attribute('src')
            db.session.add(channel)
        site.last_crawl_date = datetime.utcnow()
        db.session.add(site)
        db.session.commit()
        return True
    finally:
        webdriver_client.close()
        webdriver_client.quit()


def crawl_room_inner(channel):
    channel.rooms.update({'last_active': False})
    current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel.url))
    webdriver_client = get_webdriver_client()
    try:
        try:
            webdriver_client.get(channel.url)
        except TimeoutException:
            current_app.logger.error('调用接口失败: 内容获取失败')
            return False
        try:
            webdriver_client.find_element_by_xpath('//p[@class=\'no-videoList-title\']')
            return True
        except NoSuchElementException:
            pass
        try:
            div_element = webdriver_client.find_element_by_xpath('//div[contains(@class, \'tabc\') and contains(@class, \'active\')]')
            gameid = div_element.get_attribute('data-id')
            cnt = div_element.get_attribute('data-cnt')
            if not gameid and not cnt:
                raise NoSuchElementException('normal tab')
        except NoSuchElementException:
            for script in webdriver_client.find_elements_by_tag_name('script'):
                if 'window.gameId' in script.get_attribute('innerHTML'):
                    for script_row in script.get_attribute('innerHTML').split('\n'):
                        if 'window.gameId' in script_row:
                            gameid = script_row[script_row.find('=')+1:script_row.find(';')].strip()
                        elif 'cnt' in script_row:
                            lastindex = script_row.rfind(',') if script_row.find('//') < 0 else script_row.find('//')
                            cnt = script_row[script_row.find(':')+1:lastindex].strip()
        if 'gameid' not in dir() or 'cnt' not in dir():
            current_app.logger.error('获取房间信息解析失败，找不到gameid & cnt，重试...')
            return False
        webdriver_client.get('{}/api/static/game.lives/{}/{}-1.json'.format(channel.site.url, gameid, cnt))
        room_live_json = webdriver_client.find_element_by_tag_name('body').get_attribute('innerHTML')
        if '系统错误' in room_live_json:
            current_app.logger.error('获取房间信息解析失败，重试')
            return False
        try:
            room_live_json = json.loads(room_live_json)
        except ValueError:
            current_app.logger.error('获取房间信息解析失败，{}'.format(room_live_json))
            return True
        room_crawl_results = room_live_json['data']['rooms']
        # 遍历房间，更新数据库
        for room_crawl_result in room_crawl_results:
            room = LiveTVRoom.query.filter_by(officeid=room_crawl_result['code']).one_or_none()
            if not room:
                room = LiveTVRoom(officeid=room_crawl_result['code'])
                current_app.logger.info('新增房间 {}:{}'.format(room_crawl_result['code'], room_crawl_result['title']))
            else:
                current_app.logger.info('更新房间 {}:{}'.format(room_crawl_result['code'], room_crawl_result['title']))
            room.channel = channel
            room.name = room_crawl_result['title']
            room.url = channel.site.url + room_crawl_result['url']
            room.boardcaster = room_crawl_result['nickname']
            room.popularity = int(room_crawl_result['online'])
            room.follower = room_crawl_result['follows']
            room.last_active = True
            room.last_crawl_date = datetime.utcnow()
            room_data = LiveTVRoomData(room=room, popularity=room.popularity, follower=room.follower)
            db.session.add(room, room_data)
        channel.range = len(room_crawl_results) - channel.roomcount
        channel.roomcount = len(room_crawl_results)
        channel.last_crawl_date = datetime.utcnow()
        channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
        db.session.add(channel, channel_data)
        db.session.commit()
        return True
    finally:
        webdriver_client.close()
        webdriver_client.quit()
