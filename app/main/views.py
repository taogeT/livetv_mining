# -*- coding: UTF-8 -*-
from flask import render_template
from flask_login import login_required

from . import main, main_api
from .apis import SiteMultiple, Site, Channel, Room


@main.route('/room/index')
def room_index():
    return render_template('main/room_index.html', site_url=main_api.url_for(SiteMultiple))


@main.route('/channel/index')
def channel_index():
    return render_template('main/channel_index.html', site_url=main_api.url_for(SiteMultiple))


@main.route('/site/<int:site_id>')
def site_detail(site_id):
    """ 网站详细&频道列表 """
    return render_template('main/site.html', site_url=main_api.url_for(Site, site_id=site_id))


@main.route('/channel/<int:channel_id>')
def channel_detail(channel_id):
    """ 网站详细&频道列表 """
    return render_template('main/channel.html', channel_url=main_api.url_for(Channel, channel_id=channel_id))


@main.route('/room/<int:room_id>')
def room_detail(room_id):
    """ 网站详细&频道列表 """
    return render_template('main/room.html', room_url=main_api.url_for(Room, room_id=room_id))


@main.route('/room/search')
@login_required
def room_search():
    """ 导航栏搜索 """
    return render_template('main/search.html', site_url=main_api.url_for(SiteMultiple))
