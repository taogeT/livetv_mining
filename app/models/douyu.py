# -*- coding: UTF-8 -*-
from flask import current_app
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, \
                                       StaleElementReferenceException
from datetime import datetime

from .. import db
from . import LiveTVSite, LiveTVChannel, LiveTVRoom, get_webdirver_client


class DouyuTVChannel(db.Model, LiveTVChannel):
    __tablename__ = 'douyutvchannel'

    rooms = db.relationship('DouyuTVRoom', backref='channel', lazy='dynamic')

    @classmethod
    def scan_channel(cls, site_url):
        site = LiveTVSite.query.filter_by(scan_url=site_url).one()
        ''' 扫描频道, 目前需要弹出firefox浏览器，需改进 '''
        webdriver_client = get_webdirver_client()
        webdriver_client.get(site.scan_url)
        current_app.logger.info('扫描主目录:{}'.format(site.scan_url))
        dirul = WebDriverWait(webdriver_client, 300).until(lambda x: x.find_element_by_xpath('//ul[@id=\'live-list-contentbox\']'))
        for channel_a_element in dirul.find_elements_by_xpath('./li/a'):
            p_element = channel_a_element.find_element_by_xpath('./p')
            img_element = channel_a_element.find_element_by_xpath('./img')
            channel_name = p_element.get_attribute('innerHTML')
            channel_url = channel_a_element.get_attribute('href')
            channel = cls.query.filter_by(url=channel_url).one_or_none()
            if not channel:
                channel = cls(url=channel_url)
                current_app.logger.info('新增频道 {}:{}'.format(channel_name, channel_url))
            channel.site_id = site.id
            channel.name = channel_name
            channel.image_url = img_element.get_attribute('src')
            db.session.add(channel)
        webdriver_client.close()
        db.session.commit()


class DouyuTVRoom(db.Model, LiveTVRoom):
    __tablename__ = 'douyutvroom'
    WEIGHT_DISPLAYNAME = '鱼丸'

    channel_id = db.Column(db.Integer, db.ForeignKey('douyutvchannel.id'))

    @classmethod
    def scan_room(cls, site_scan_url=None, channel_url=None):
        if not site_scan_url and not channel_url:
            raise ValueError('At Lease input one param: site_url/channel_url')
        elif channel_url:
            channel = DouyuTVChannel.query.filter_by(url=channel_url).one()
            return cls._scan_room_inner(channel)
        elif site_scan_url:
            site = LiveTVSite.query.filter_by(scan_url=site_scan_url).one()
            channels = [channel for channel in DouyuTVChannel.query.filter_by(site_id=site.id)]
            while len(channels) > 0:
                channel = channels.pop(0)
                if not cls._scan_room_inner(channel):
                    channels.append(channel)
            return True

    @classmethod
    def _scan_room_inner(cls, channel):
        ''' 扫描房间, 目前需要弹出firefox浏览器，需改进 '''
        def scan_douyu_pager(driver):
            '''
            浏览器等待页面动态加载判断函数
            当找到'下一页'元素或不存在排序的静态代码，跳出等待
            '''
            try:
                return driver.find_element_by_class_name('shark-pager-next')
            except NoSuchElementException:
                try:
                    driver.find_element_by_id('J-pager')
                    return False
                except NoSuchElementException:
                    return True

        current_app.logger.info('开始扫描频道{}: {}'.format(channel.name, channel.url))
        webdriver_client = get_webdirver_client()
        webdriver_client.get(channel.url)
        try:
            webdriver_client.find_element_by_xpath('//div[@class=\'nonemsg\']')
            webdriver_client.close()
            return True
        except NoSuchElementException:
            pass
        room_scan_results = []
        # 查找频道内所有房间
        while True:
            try:
                nextpageele = WebDriverWait(webdriver_client, 30).until(scan_douyu_pager)
                room_a_elements = webdriver_client.find_elements_by_xpath('//ul[@id=\'live-list-contentbox\']/li/a')
                for room_a_element in room_a_elements:
                    p_elements = room_a_element.find_elements_by_xpath('./div/p/span')
                    room_scan_result = {
                        'url': room_a_element.get_attribute('href'),
                        'name': room_a_element.get_attribute('title'),
                        'boardcaster': p_elements[0].get_attribute('innerHTML'),
                    }
                    room_scan_result['popularity'] = p_elements[1].get_attribute('innerHTML')
                    if room_scan_result['popularity'].endswith('万'):
                        room_scan_result['popularity'] = int(float(room_scan_result['popularity'][:-1]) * 10000)
                    else:
                        room_scan_result['popularity'] = int(room_scan_result['popularity'])
                    room_scan_results.append(room_scan_result)
                if isinstance(nextpageele, bool) or 'shark-pager-disable' in nextpageele.get_attribute('class'):
                    break
                else:
                    nextpageele.click()
            except (TimeoutException, StaleElementReferenceException):
                current_app.logger.error('等待房间列表加载超时，遍历失败')
                webdriver_client.close()
                return False
        # 遍历房间，更新数据库
        for room_scan_result in room_scan_results:
            room = cls.query.filter_by(url=room_scan_result['url']).one_or_none()
            if not room:
                room = cls(url=room_scan_result['url'])
            room.channel = channel
            room.name = room_scan_result['name']
            room.boardcaster = room_scan_result['boardcaster']
            room.popularity = room_scan_result['popularity']
            room_url_lastpath = room.url.split('/')[-1]
            if room_url_lastpath.isdigit():
                room.officeid = int(room_url_lastpath)
            room.last_scan_date = datetime.utcnow()
            db.session.add(room)
        channel.range = len(room_scan_results) - channel.roomcount
        channel.roomcount = len(room_scan_results)
        channel.last_scan_date = datetime.utcnow()
        db.session.add(channel)
        db.session.commit()
        webdriver_client.close()
        return True
