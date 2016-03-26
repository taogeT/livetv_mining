# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, \
                                       StaleElementReferenceException
from datetime import datetime

from .. import db
from . import LiveTVSite, LiveTVChannel, LiveTVRoom, get_webdirver_client

import json
import math


class ZhanqiTVChannel(db.Model, LiveTVChannel):
    __tablename__ = 'zhanqitvchannel'

    rooms = db.relationship('ZhanqiTVRoom', backref='channel', lazy='dynamic')

    @classmethod
    def scan_channel(cls, site_url):
        site = LiveTVSite.query.filter_by(scan_url=site_url).one()
        ''' 扫描频道, 目前需要弹出firefox浏览器，需改进 '''
        webdriver_client = get_webdirver_client()
        webdriver_client.get(site.scan_url)
        current_app.logger.info('扫描主目录:{}'.format(site.scan_url))
        dirul = WebDriverWait(webdriver_client, 300).until(lambda x: x.find_element_by_xpath('//ul[@id=\'game-list-panel\']'))
        for channel_a_element in dirul.find_elements_by_xpath('./li/div/a'):
            p_element = channel_a_element.find_element_by_xpath('./p')
            img_element = channel_a_element.find_element_by_xpath('./img')
            channel_name = p_element.get_attribute('innerHTML')
            channel_url = channel_a_element.get_attribute('href')
            channel = cls.query.filter_by(url=channel_url).one_or_none()
            if not channel:
                channel = cls(url=channel_url)
                current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
            else:
                current_app.logger.info('更新频道 {}:{}'.format(channel_name, channel_url))
            channel.site_id = site.id
            channel.name = channel_name
            channel.image_url = img_element.get_attribute('src')
            channel.icon_url = img_element.get_attribute('src')
            channel.last_scan_date = datetime.utcnow()
            db.session.add(channel)
        webdriver_client.close()
        db.session.commit()


class ZhanqiTVRoom(db.Model, LiveTVRoom):
    __tablename__ = 'zhanqitvroom'

    channel_id = db.Column(db.Integer, db.ForeignKey('zhanqitvchannel.id'))

    @classmethod
    def scan_room(cls, site_scan_url=None, channel_url=None):
        if not site_scan_url and not channel_url:
            raise ValueError('At Lease input one param: site_url/channel_url')
        elif channel_url:
            channel = ZhanqiTVChannel.query.filter_by(url=channel_url).one()
            site = LiveTVSite.query.get(channel.site_id)
            return cls._scan_room_inner(channel, site.url)
        elif site_scan_url:
            site = LiveTVSite.query.filter_by(scan_url=site_scan_url).one()
            channels = [channel for channel in ZhanqiTVChannel.query.filter_by(site_id=site.id)]
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
        try:
            webdriver_client.find_element_by_xpath('//p[@class=\'no-videoList-title\']')
            webdriver_client.close()
            return True
        except NoSuchElementException:
            pass
        # 查找信息div[contains(@class, 'demo') and contains(@class, 'other')]
        try:
            div_element = webdriver_client.find_element_by_xpath('//div[contains(@class, \'tabc\') and contains(@class, \'active\')]')
            gameid = div_element.get_attribute('data-id')
            cnt = div_element.get_attribute('data-cnt')
            if not gameid and not cnt:
                raise NoSuchElementException('normal tab')
        except NoSuchElementException:
            # 查找频道内所有script，找到排序
            for script in webdriver_client.find_elements_by_tag_name('script'):
                if 'window.gameId' in script.get_attribute('innerHTML'):
                    for script_row in script.get_attribute('innerHTML').split('\n'):
                        if 'window.gameId' in script_row:
                            gameid = script_row[script_row.find('=')+1:script_row.find(';')].strip()
                        elif 'cnt' in script_row:
                            lastindex = script_row.rfind(',') if script_row.find('//') < 0 else script_row.find('//')
                            cnt = script_row[script_row.find(':')+1:lastindex]
        if 'gameid' not in dir() or 'cnt' not in dir():
            webdriver_client.close()
            return False
        else:
            a, b = math.frexp(float(cnt))
            a = math.ceil(a)
            size = int(math.ldexp(a, b))
        webdriver_client.get(site_url + '/api/static/game.lives/{}/{}-1.json'.format(gameid, size))
        room_live_json = webdriver_client.find_element_by_tag_name('body').text
        if '系统错误' in room_live_json:
            webdriver_client.close()
            return False
        try:
            room_live_json = json.loads(room_live_json)
        except ValueError:
            current_app.logger.error('获取房间信息解析失败，重试')
            webdriver_client.close()
            return False
        room_scan_results = room_live_json['data']['rooms']
        # 遍历房间，更新数据库
        for room_scan_result in room_scan_results:
            room_scan_result['url'] = site_url + room_scan_result['url']
            room = cls.query.filter_by(url=room_scan_result['url']).one_or_none()
            if not room:
                room = cls(url=room_scan_result['url'])
                current_app.logger.info('新增房间 {}:{}'.format(room_scan_result['code'], room_scan_result['title']))
            else:
                current_app.logger.info('更新房间 {}:{}'.format(room_scan_result['code'], room_scan_result['title']))
            room.channel = channel
            room.name = room_scan_result['title']
            room.boardcaster = room_scan_result['nickname']
            room.popularity = int(room_scan_result['online'])
            room.officeid = room_scan_result['code']
            room.follower = room_scan_result['follows']
            room.last_scan_date = datetime.utcnow()
            db.session.add(room)
        channel.range = len(room_scan_results) - channel.roomcount
        channel.roomcount = len(room_scan_results)
        channel.last_scan_date = datetime.utcnow()
        db.session.add(channel)
        db.session.commit()
        webdriver_client.close()
        return True
