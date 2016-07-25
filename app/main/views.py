# -*- coding: UTF-8 -*-
from flask import render_template, request, current_app
from sqlalchemy import and_
from datetime import datetime, timedelta

from .forms import SearchRoomForm
from . import main
from ..models import LiveTVSite, LiveTVChannel, LiveTVRoom, LiveTVHost, \
                    LiveTVChannelData, LiveTVRoomData

import pytz


@main.route('/sites')
def sites_index():
    """ 直播网站列表 """
    sites = []
    for site in LiveTVSite.query.filter_by(valid=True).order_by(LiveTVSite.order_int.asc()).all():
        site.roomtop = site.rooms.filter_by(openstatus=True).order_by(LiveTVRoom.online.desc())
        sites.append(site)
    return render_template('main/sites_index.html', sites=sites)


@main.route('/channels')
def channels_index():
    """ 直播频道列表 """
    sites = []
    for site in LiveTVSite.query.filter_by(valid=True).order_by(LiveTVSite.order_int.asc()).all():
        site.channeltop = site.channels.filter_by(valid=True).order_by(LiveTVChannel.room_total.desc())
        sites.append(site)
    return render_template('main/channels_index.html', sites=sites)


@main.route('/site/<int:site_id>')
def site(site_id):
    """ 网站详细&频道列表 """
    site = LiveTVSite.query.get_or_404(site_id)
    page = request.args.get('page', 1, type=int)
    pagination = site.channels.filter_by(valid=True)\
        .order_by(LiveTVChannel.room_total.desc(), LiveTVChannel.room_range.desc()).paginate(
            page = page, error_out = False,
            per_page = current_app.config['FLASK_CHANNELS_PER_PAGE'])
    channels = pagination.items
    return render_template('main/site.html', channels=channels, pagination=pagination, site=site)


@main.route('/channel/<int:channel_id>')
def channel(channel_id):
    """ 频道详细&房间列表 """
    channel = LiveTVChannel.query.get_or_404(channel_id)
    page = request.args.get('page', 1, type=int)
    pagination = channel.rooms.filter_by(openstatus=True).order_by(LiveTVRoom.online.desc()) \
                        .paginate(page=page, error_out=False,
                                  per_page=current_app.config['FLASK_ROOMS_PER_PAGE'])
    rooms = pagination.items
    current_time = datetime.utcnow()
    current_date = datetime(current_time.year, current_time.month, current_time.day)
    compare_date = current_date - timedelta(days=1)
    channel_dataset = channel.dataset.filter(LiveTVChannelData.create_date > compare_date) \
                             .filter(LiveTVChannelData.create_date <= current_date) \
                             .order_by(LiveTVChannelData.create_date.desc()).all()
    chart_x_axis = []
    chart_y_axis = []
    split_delta = timedelta(hours=2)
    while compare_date < current_date:
        compare_next_date = compare_date + split_delta
        mark_date = compare_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        chart_x_axis.append(mark_date.strftime('%H:%M'))
        chart_y_axis.append(0)
        chart_y_count = 0
        while len(channel_dataset) > 0:
            channel_data = channel_dataset.pop()
            if compare_date < channel_data.create_date <= compare_next_date:
                chart_y_axis[-1] += channel_data.room_total
                chart_y_count += 1
            elif channel_data.create_date > compare_next_date:
                channel_dataset.append(channel_data)
                break
        if chart_y_count > 0:
            chart_y_axis[-1] /= chart_y_count
        compare_date += split_delta
    return render_template('main/channel.html', channel=channel, rooms=rooms, pagination=pagination,
                                                   chart_axis=(chart_x_axis, chart_y_axis))


@main.route('/room/<int:room_id>')
def room(room_id):
    """ 房间详细 """
    room = LiveTVRoom.query.get_or_404(room_id)
    current_time = datetime.utcnow()
    current_date = datetime(current_time.year, current_time.month, current_time.day)
    compare_date = current_date - timedelta(days=1)
    room_dataset = room.dataset.filter(LiveTVRoomData.create_date > compare_date) \
        .filter(LiveTVRoomData.create_date <= current_date) \
        .order_by(LiveTVRoomData.create_date.desc()).all()
    chart_x_axis = []
    chart_y_axis = []
    split_delta = timedelta(hours=1, minutes=30)
    while compare_date < current_date:
        compare_next_date = compare_date + split_delta
        mark_date = compare_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
        chart_x_axis.append(mark_date.strftime('%H:%M'))
        chart_y_axis.append(0)
        chart_y_count = 0
        while len(room_dataset) > 0:
            channel_data = room_dataset.pop()
            if compare_date < channel_data.create_date <= compare_next_date:
                chart_y_axis[-1] += channel_data.online
                chart_y_count += 1
            elif channel_data.create_date > compare_next_date:
                room_dataset.append(channel_data)
                break
        if chart_y_count > 0:
            chart_y_axis[-1] /= chart_y_count
        compare_date += split_delta
    return render_template('main/room.html', room=room, chart_axis=(chart_x_axis, chart_y_axis))


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
