# -*- coding: UTF-8 -*-
from flask import render_template, request, current_app

from . import main
from ..models import LiveTVSite, LiveTVChannel, LiveTVRoom


@main.route('/index')
def index():
    ''' 直播网站列表 '''
    sites = [site for site in LiveTVSite.query.filter_by(valid=True).order_by(LiveTVSite.order_int.asc())]
    return render_template('index.html', sites=sites)


@main.route('/site/<int:site_id>')
def site(site_id):
    ''' 网站详细&频道列表 '''
    site = LiveTVSite.query.get_or_404(site_id)
    page = request.args.get('page', 1, type=int)
    pagination = site.channels.order_by(LiveTVChannel.roomcount.desc()).paginate(
            page=page,  error_out=False,
            per_page=current_app.config['FLASKY_CHANNELS_PER_PAGE'])
    channels = pagination.items
    title_dict = {'name': LiveTVChannel.name.doc,
                  'url': LiveTVChannel.url.doc,
                  'image_url': LiveTVChannel.image_url.doc,
                  'last_crawl_date': LiveTVChannel.last_crawl_date.doc,
                  'roomcount': LiveTVChannel.roomcount.doc,
                  'range': LiveTVChannel.range.doc}
    return render_template('site.html', channels=channels, pagination=pagination,
                           title_dict=title_dict, site=site)


@main.route('/channel/<int:channel_id>')
def channel(channel_id):
    ''' 频道详细&房间列表 '''
    channel = LiveTVChannel.query.get_or_404(channel_id)
    page = request.args.get('page', 1, type=int)
    pagination = channel.rooms.filter_by(last_active=True) \
                        .order_by(LiveTVRoom.popularity.desc()).paginate(
                    page=page,  error_out=False,
                    per_page=current_app.config['FLASKY_ROOMS_PER_PAGE'])
    rooms = pagination.items
    title_dict = {'name': LiveTVRoom.name.doc,
                  'url': LiveTVRoom.url.doc,
                  'popularity': LiveTVRoom.popularity.doc,
                  'last_crawl_date': LiveTVRoom.last_crawl_date.doc,
                  'boardcaster': LiveTVRoom.boardcaster.doc,
                  'follower': LiveTVRoom.follower.doc,
                  'officeid': LiveTVRoom.officeid.doc}
    return render_template('channel.html', channel=channel, rooms=rooms,
                           pagination=pagination, title_dict=title_dict)


@main.route('/room/<int:room_id>')
def room(room_id):
    ''' 房间详细 '''
    room = LiveTVRoom.query.get_or_404(room_id)
    return render_template('room.html', room=room)


@main.route('/about-me')
def about_me():
    ''' 关于我 '''
    return 'Building...'
