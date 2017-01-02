# -*- coding: UTF-8 -*-
from flask import g
from flask_login import login_required

from . import rest_api as subscribe_api, Resource


@subscribe_api.resource('/subscribe')
class Subscribe(Resource):

    method_decorators = [login_required]

    def get(self):
        rooms = {}
        subscribe_count = 0
        for room in g.user.rooms.all():
            if room.site.name in rooms:
                rooms[room.site.name].append(room)
            else:
                rooms[room.site.name] = [room]
            subscribe_count += 1
        return {
            'rooms': rooms,
            'subscribe_count': subscribe_count,
            'subscribe_max': g.user.subscribe_max
        }
