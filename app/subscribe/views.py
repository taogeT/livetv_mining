# -*- coding: UTF-8 -*-
from flask import render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user

from . import subscribe
from .forms import SubscribeRoomForm
from .. import db
from ..models import LiveTVRoom


@subscribe.route('/list', methods=['GET', 'POST'])
@login_required
def slist():
    form = SubscribeRoomForm()
    if form.validate_on_submit():
        room = LiveTVRoom.query.filter_by(url=form.roomurl.data).one_or_none()
        if not room:
            flash('找不到对应的房间记录，请检查URL是否正确', category='error')
        elif current_user.rooms.count() >= current_user.subscribe_max:
            flash('订阅数已满，无法订阅新房间', category='error')
        else:
            current_user.rooms.append(room)
            db.session.add(current_user)
            db.session.commit()
        return redirect(url_for('subscribe.slist'))
    rooms = {}
    subscribe_count = 0
    for room in current_user.rooms:
        if room.site.name in rooms:
            rooms[room.site.name].append(room)
        else:
            rooms[room.site.name] = [room]
        subscribe_count += 1
    return render_template('subscribe/list.html', rooms=rooms.items(), subscribe_count=subscribe_count, form=form)
