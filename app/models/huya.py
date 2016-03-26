# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

from .. import db
from . import LiveTVSite, LiveTVChannel, LiveTVRoom, get_webdirver_client

import json


class HuyaTVChannel(db.Model, LiveTVChannel):
    __tablename__ = 'huyatvchannel'

    rooms = db.relationship('HuyaTVRoom', backref='channel', lazy='dynamic')

    @classmethod
    def scan_channel(cls, site_url):
        site = LiveTVSite.query.filter_by(scan_url=site_url).one()
        ''' 扫描频道, 目前需要弹出firefox浏览器，需改进 '''
        webdriver_client = get_webdirver_client()
        webdriver_client.get(site.scan_url)
        current_app.logger.info('扫描主目录:{}'.format(site.scan_url))
        dirul = WebDriverWait(webdriver_client, 300).until(lambda x: x.find_element_by_xpath('//ul[@class=\'game-list\']'))
        for channel_a_element in dirul.find_elements_by_xpath('./li/a[contains(@class, \'pic\') and contains(@class, \'clickstat\')]'):
            img_element = channel_a_element.find_element_by_xpath('./img')
            channel_name = img_element.get_attribute('title')
            channel_url = channel_a_element.get_attribute('href')
            channel = cls.query.filter_by(url=channel_url).one_or_none()
            if not channel:
                channel = cls(url=channel_url)
                current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
            else:
                current_app.logger.info('更新频道 {}:{}'.format(channel_name, channel_url))
            channel.site_id = site.id
            channel.name = channel_name
            image_url = img_element.get_attribute('data-original')
            if not image_url:
                image_url = img_element.get_attribute('src')
            channel.image_url = image_url
            channel.icon_url = image_url
            channel.last_scan_date = datetime.utcnow()
            db.session.add(channel)
        webdriver_client.close()
        db.session.commit()


class HuyaTVRoom(db.Model, LiveTVRoom):
    __tablename__ = 'huyatvroom'

    channel_id = db.Column(db.Integer, db.ForeignKey('huyatvchannel.id'))

    @classmethod
    def scan_room(cls, site_scan_url=None, channel_url=None):
        if not site_scan_url and not channel_url:
            raise ValueError('At Lease input one param: site_url/channel_url')
        elif channel_url:
            channel = HuyaTVChannel.query.filter_by(url=channel_url).one()
            site = LiveTVSite.query.get(channel.site_id)
            return cls._scan_room_inner(channel, site.url)
        elif site_scan_url:
            site = LiveTVSite.query.filter_by(scan_url=site_scan_url).one()
            channels = [channel for channel in HuyaTVChannel.query.filter_by(site_id=site.id)]
            while len(channels) > 0:
                channel = channels.pop(0)
                if not cls._scan_room_inner(channel, site.url):
                    channels.append(channel)
            return True

    @classmethod
    def _scan_room_inner(cls, channel, site_url):
        ''' 扫描房间 '''
        current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel.url))
        webdriver_client = get_webdirver_client()
        webdriver_client.get(channel.url)
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
        room_scan_url = site_url + '/index.php?m=Game&do=ajaxGameLiveByPage&gid={}&page={{}}'.format(gameid)
        page_num, page_limit = 1, 20
        scan_room_count = 0
        while True:
            webdriver_client.get(room_scan_url.format(page_num))
            try:
                room_live_json = json.loads(webdriver_client.find_element_by_tag_name('body').text)
            except ValueError:
                current_app.logger.error('获取房间信息解析失败，重试')
                continue
            room_scan_results = room_live_json['data']['list']
            for room_scan_result in room_scan_results:
                room_scan_result['url'] = site_url + '/' + room_scan_result['privateHost']
                room = cls.query.filter_by(url=room_scan_result['url']).one_or_none()
                if not room:
                    room = cls(url=room_scan_result['url'])
                    current_app.logger.info('新增房间:{}'.format(room_scan_result['roomName']))
                else:
                    current_app.logger.info('更新房间:{}'.format(room_scan_result['roomName']))
                room.channel = channel
                room.name = room_scan_result['roomName']
                room.boardcaster = room_scan_result['nick']
                room.last_scan_date = datetime.utcnow()
                db.session.add(room)
            scan_room_count += len(room_scan_results)
            if len(room_scan_results) < page_limit:
                break
            else:
                page_num += 1
        channel.range = len(room_scan_results) - channel.roomcount
        channel.roomcount = len(room_scan_results)
        channel.last_scan_date = datetime.utcnow()
        db.session.add(channel)
        db.session.commit()
        webdriver_client.close()
        return True
