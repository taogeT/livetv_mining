# -*- coding: UTF-8 -*-
from flask import render_template, request, current_app

from . import main
from ..models import LiveTVSite, get_instance_class


@main.route('/site')
def site():
    ''' 直播网站列表 '''
    sites = []
    for site in LiveTVSite.query.filter_by(valid=True).order_by(LiveTVSite.weight.desc()):
        channel_class, room_class = get_instance_class(site.name)
        site.channels = channel_class.query.filter_by(site_id=site.id) \
                                     .order_by(channel_class.roomcount.desc())
        sites.append(site)
    return render_template('site.html', sites=sites)


@main.route('/site/<int:site_id>/channel')
def channel(site_id):
    ''' 频道列表 '''
    site = LiveTVSite.query.get_or_404(site_id)
    channel_class, room_class = get_instance_class(site.name)
    site.channel_count = channel_class.query.filter_by(site_id=site.id).count()
    page = request.args.get('page', 1, type=int)
    pagination = channel_class.query.filter_by(site_id=site.id) \
        .order_by(channel_class.roomcount.desc()).paginate(
            page=page,  error_out=False,
            per_page=current_app.config['FLASKY_CHANNELS_PER_PAGE'])
    channels = pagination.items
    title_dict = {'name': channel_class.name.doc,
                  'url': channel_class.url.doc,
                  'image_url': channel_class.image_url.doc,
                  'last_scan_date': channel_class.last_scan_date.doc,
                  'roomcount': channel_class.roomcount.doc,
                  'range': channel_class.range.doc}
    return render_template('channel.html', channels=channels, pagination=pagination,
                           title_dict=title_dict, site=site)


@main.route('/<string:site_name>/channel/<int:channel_id>/room')
def channel_room(site_name, channel_id):
    ''' 房间列表 '''
    site = LiveTVSite.query.filter_by(name=site_name).one()
    channel_class, room_class = get_instance_class(site_name)
    channel = channel_class.query.get_or_404(channel_id)
    page = request.args.get('page', 1, type=int)
    pagination = channel.rooms.order_by(room_class.popularity.desc()).paginate(
                    page=page,  error_out=False,
                    per_page=current_app.config['FLASKY_ROOMS_PER_PAGE'])
    rooms = pagination.items
    title_dict = {'name': room_class.name.doc,
                  'url': room_class.url.doc,
                  'popularity': room_class.popularity.doc,
                  'last_scan_date': room_class.last_scan_date.doc,
                  'boardcaster': room_class.boardcaster.doc,
                  'officeid': room_class.officeid.doc}
    return render_template('room.html', channel=channel, rooms=rooms, site=site,
                           pagination=pagination, title_dict=title_dict)


@main.route('/about-me')
def about_me():
    ''' 关于我 '''
    return 'Building...'
