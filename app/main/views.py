# -*- coding: UTF-8 -*-
from flask import render_template, request, current_app, redirect, url_for

from . import main
from .forms import SearchRoomForm
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
    return render_template('site.html', channels=channels, pagination=pagination,
                           title_dict=LiveTVChannel.title(), site=site)


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
    return render_template('channel.html', channel=channel, rooms=rooms,
                           pagination=pagination, title_dict=LiveTVRoom.title())


@main.route('/room/<int:room_id>')
def room(room_id):
    ''' 房间详细 '''
    room = LiveTVRoom.query.get_or_404(room_id)
    return render_template('room.html', room=room)


@main.route('/search', methods=['GET', 'POST'])
def search():
    ''' 导航栏搜索 '''
    page = request.args.get('page', 1, type=int)
    form = SearchRoomForm()
    form.site_name.choices = [(site.name, site.displayname) for site in LiveTVSite.query.filter_by(valid=True)]
    if form.validate_on_submit():
        pagination = LiveTVRoom.query.join(LiveTVChannel).join(LiveTVSite) \
                               .filter(LiveTVSite.name == form.site_name.data) \
                               .filter(LiveTVRoom.last_active == form.only_active.data) \
                               .order_by(LiveTVRoom.popularity.desc())
        if form.boardcaster.data:
            pagination = pagination.filter(LiveTVRoom.boardcaster.like('%{}%'.format(form.boardcaster.data)))
        if form.room_name.data:
            pagination = pagination.filter(LiveTVRoom.name.like('%{}%'.format(form.room_name.data)))
        pagination = pagination.paginate(page=page,  error_out=False,
                                         per_page=current_app.config['FLASKY_SEARCH_PER_PAGE'] + 1)
        rooms = pagination.items
        return render_template('search.html', rooms=rooms, form=form,
                               pagination=pagination, title_dict=LiveTVRoom.title(),
                               over_query_count=len(rooms) > current_app.config['FLASKY_SEARCH_PER_PAGE'])
    return render_template('search.html', form=form, rooms=[], pagination=None,
                           title_dict=LiveTVRoom.title(), over_query_count=False)


@main.route('/about-me')
def about_me():
    ''' 关于我 '''
    return 'Building...'
