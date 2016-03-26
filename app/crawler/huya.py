# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import datetime

from .. import db
from ..models import LiveTVChannel, LiveTVRoom, LiveTVChannelData
from . import get_webdirver_client

import json


def crawl_channel_inner(site):
    webdriver_client = get_webdirver_client()
    webdriver_client.get(site.crawl_url)
    current_app.logger.info('扫描主目录:{}'.format(site.crawl_url))
    dirul = WebDriverWait(webdriver_client, 300).until(lambda x: x.find_element_by_xpath('//ul[@class=\'game-list\']'))
    for channel_a_element in dirul.find_elements_by_xpath('./li/a[contains(@class, \'pic\') and contains(@class, \'clickstat\')]'):
        img_element = channel_a_element.find_element_by_xpath('./img')
        channel_name = img_element.get_attribute('title')
        channel_url = channel_a_element.get_attribute('href')
        channel = LiveTVChannel.query.filter_by(url=channel_url).one_or_none()
        if not channel:
            channel = LiveTVChannel(url=channel_url)
            current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
        else:
            current_app.logger.info('更新频道 {}:{}'.format(channel_name, channel_url))
        channel.site = site
        channel.name = channel_name
        image_url = img_element.get_attribute('data-original')
        if not image_url:
            image_url = img_element.get_attribute('src')
        channel.image_url = image_url
        channel.icon_url = image_url
        db.session.add(channel)
    site.last_crawl_date = datetime.utcnow()
    db.session.add(site)
    db.session.commit()
    webdriver_client.close()


def crawl_room_inner(channel):
    current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel.url))
    webdriver_client = get_webdirver_client()
    try:
        webdriver_client.get(channel.url)
    except TimeoutException:
        current_app.logger.error('打开频道URL失败，重试')
        webdriver_client.close()
        return False
    script_element = webdriver_client.find_element_by_xpath('//script[@data-fixed="true"]')
    gameid = None
    for script_row in script_element.get_attribute('innerHTML').split('\n'):
        if 'window.gameId' in script_row:
            gameid = script_row[script_row.find('=') + 1:script_row.find(';')].strip()
            break
        elif 'var GID' in script_row:
            gameid = script_row[script_row.find('=') + 1:script_row.rfind(';')].strip()
            if gameid.startswith('\''):
                gameid = gameid[1:-1]
            break
    if not gameid:
        current_app.logger.error('获取频道gameid失败，重试')
        webdriver_client.close()
        return False
    room_crawl_url = '{}/index.php?m=Game&do=ajaxGameLiveByPage&gid={}&page={{}}'.format(channel.site.url, gameid)
    page_num, page_limit = 1, 20
    crawl_room_count = 0
    current_app.logger.info('获取房间列表: {}'.format(room_crawl_url))
    while True:
        webdriver_client.get(room_crawl_url.format(page_num))
        try:
            room_live_json = json.loads(webdriver_client.find_element_by_tag_name('body').text)
        except ValueError:
            current_app.logger.error('获取房间信息解析失败，重试 {}'.format(room_crawl_url))
            page_num += 1
            continue
        room_crawl_results = room_live_json['data']['list']
        for room_crawl_result in room_crawl_results:
            room_crawl_result['url'] = '{}/{}'.format(channel.site.url, room_crawl_result['privateHost'])
            room = LiveTVRoom.query.filter_by(url=room_crawl_result['url']).one_or_none()
            if not room:
                room = LiveTVRoom(url=room_crawl_result['url'])
                current_app.logger.info('新增房间:{}'.format(room_crawl_result['roomName']))
            else:
                current_app.logger.info('更新房间:{}'.format(room_crawl_result['roomName']))
            room.channel = channel
            room.name = room_crawl_result['roomName']
            room.boardcaster = room_crawl_result['nick']
            room.last_crawl_date = datetime.utcnow()
            db.session.add(room)
        crawl_room_count += len(room_crawl_results)
        if len(room_crawl_results) < page_limit:
            break
        else:
            page_num += 1
    channel.range = crawl_room_count - channel.roomcount
    channel.roomcount = crawl_room_count
    channel.last_crawl_date = datetime.utcnow()
    channel_data = LiveTVChannelData(channel=channel, roomcount=channel.roomcount)
    db.session.add(channel, channel_data)
    db.session.commit()
    webdriver_client.close()
    return True
