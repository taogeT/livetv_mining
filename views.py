# -*- coding: UTF-8 -*-
from markdown import markdown
from flask import render_template, request, current_app
from sqlalchemy import and_
from datetime import datetime, timedelta

from .forms import SearchRoomForm
from . import crawler
from .models import LiveTVSite, LiveTVChannel, LiveTVRoom, LiveTVHost, \
                    LiveTVChannelData

import codecs
import os


@crawler.route('/')
def index():
    """ 直播网站列表 """
    sites = []
    for site in LiveTVSite.query.filter_by(valid=True).order_by(LiveTVSite.order_int.asc()):
        site.roomtop = site.rooms.filter_by(openstatus=True).order_by(LiveTVRoom.online.desc())
        site.channeltop = site.channels.filter_by(valid=True).order_by(LiveTVChannel.room_total.desc(), LiveTVChannel.room_range.desc())
        sites.append(site)
    return render_template('crawler/index.html', sites=sites)


@crawler.route('/site/<int:site_id>')
def site(site_id):
    """ 网站详细&频道列表 """
    site = LiveTVSite.query.get_or_404(site_id)
    page = request.args.get('page', 1, type=int)
    pagination = site.channels.filter_by(valid=True)\
        .order_by(LiveTVChannel.room_total.desc(), LiveTVChannel.room_range.desc()).paginate(
            page = page, error_out = False,
            per_page = current_app.config['FLASK_CHANNELS_PER_PAGE'])
    channels = pagination.items
    return render_template('crawler/site.html', channels=channels, pagination=pagination, site=site)


@crawler.route('/channel/<int:channel_id>')
def channel(channel_id):
    """ 频道详细&房间列表 """
    channel = LiveTVChannel.query.get_or_404(channel_id)
    page = request.args.get('page', 1, type=int)
    pagination = channel.rooms.filter_by(openstatus=True).order_by(LiveTVRoom.online.desc()) \
                        .paginate(page=page, error_out=False,
                                  per_page=current_app.config['FLASK_ROOMS_PER_PAGE'])
    rooms = pagination.items
    current_time = datetime.utcnow()
    datetime(current_time.year, current_time.month, current_time.day)
    #channel.dataset.filter(LiveTVChannelData.create_date > )

    #datetime.combine()

    return render_template('crawler/channel.html', channel=channel, rooms=rooms, pagination=pagination)


@crawler.route('/room/<int:room_id>')
def room(room_id):
    """ 房间详细 """
    room = LiveTVRoom.query.get_or_404(room_id)
    return render_template('crawler/room.html', room=room)


@crawler.route('/search', methods=['GET', 'POST'])
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
        return render_template('crawler/search.html', rooms=rooms, form=form)
    return render_template('crawler/search.html', form=form, rooms=[], over_query_count=False)


@crawler.route('/about')
def about():
    """ 关于 """
    with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as mdf:
        mdhtml = markdown(mdf.read())
    return render_template('crawler/about.html', mdhtml=mdhtml)
