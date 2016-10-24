# -*- coding: UTF-8 -*-
from flask import render_template, request, current_app
from sqlalchemy import and_
from datetime import datetime, timedelta

from .forms import SearchRoomForm
from . import main, main_api
from .apis import SiteMultiple, Site, Channel, Room, Search

import pytz


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
def room_search():
    """ 导航栏搜索 """
    return render_template('main/search.html', room_url=main_api.url_for(Search))

'''
@main.route('/search', methods=['GET', 'POST'])
def search():
    """ 导航栏搜索 """
    form = SearchRoomForm()
    if form.validate_on_submit():
        form_condition = and_()
        if form.room_name.data:
            form_condition.append(LiveTVRoom.name.like('%{}%'.format(form.room_name.data)))
        if form.host_nickname.data:
            host_id_list = [host.id for host in list(LiveTVHost.query.filter(LiveTVHost.nickname.like('%{}%'.format(form.host_nickname.data))))]
            form_condition.append(LiveTVRoom.host_id.in_(host_id_list))
        rooms = []
        for codefield in form.site_code.form:
            if codefield.data:
                subname = codefield.name[codefield.name.find(form.site_code.separator) + 1:]
                pagination = LiveTVRoom.query.join(LiveTVSite) \
                                       .filter(LiveTVSite.code == subname) \
                                       .filter(LiveTVRoom.openstatus == True) \
                                       .filter(form_condition) \
                                       .order_by(LiveTVRoom.online.desc()) \
                                       .paginate(page=1, error_out=False,
                                                 per_page=current_app.config['FLASK_SEARCH_PER_PAGE'])
                rooms.append((codefield.label.text, pagination.items))
        return render_template('main/search.html', rooms=rooms, form=form)
    return render_template('main/search.html', form=form, rooms=[], over_query_count=False)

'''
