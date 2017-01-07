# -*- coding: UTF-8 -*-
from flask import request, g
from flask_login import login_required

from . import restful_api as subscribe_api, Resource
from .. import db
from ..models import LiveTVRoom


@subscribe_api.resource('/subscribe/room')
class Subscribe(Resource):

    method_decorators = [login_required]

    def get(self):
        rooms = {}
        subscribe_count = 0
        for room in g.user.rooms.all():
            if room.site.name in rooms:
                rooms[room.site.name].append(room.to_dict())
            else:
                rooms[room.site.name] = [room.to_dict()]
            subscribe_count += 1
        return {
            'rooms': rooms,
            'subscribe_count': subscribe_count
        }

    def post(self):
        room_url = request.data.get('url', '')
        if not room_url:
            return {'message': '请先输入房间URL'}, 400
        room = LiveTVRoom.query.filter_by(url=room_url).one_or_none()
        if not room:
            return {'message': '找不到对应的房间记录，请检查URL是否正确'}, 400
        elif g.user.rooms.count() >= g.user.subscription:
            return {'message': '订阅数已满，无法订阅新房间'}, 400
        else:
            g.user.rooms.append(room)
            db.session.add(g.user)
            db.session.commit()
        return {'site': room.site.name, 'room': room.to_dict()}

    def delete(self):
        room_id = request.data.get('id', None, type=int)
        if not room_id:
            return {'message': '请先输入房间ID'}, 400

        room = LiveTVRoom.query.get(room_id)
        if not room:
            return {'message': '找不到对应的房间记录，请检查ID是否正确'}, 400
        else:
            g.user.rooms.remove(room)
            db.session.add(g.user)
            db.session.commit()
        return {}
