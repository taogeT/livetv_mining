# -*- coding: UTF-8 -*-
from flask import render_template, g
from flask_login import login_required

from .. import db
from . import subscribe


@subscribe.route('/list')
@login_required
def slist():
    rooms = {}
    for room in g.user.rooms:
        if room.site.name in rooms:
            rooms[room.site.name].append(room)
        else:
            rooms[room.site.name] = [room]
    return render_template('subscribe/list.html', rooms=rooms.items())
