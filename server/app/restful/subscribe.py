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
        return [room.to_dict() for room in g.user.rooms.all()]

    def post(self):
        room_url = (request.get_json() if request.json else request.values).get('url', '')
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
        return room.to_dict()


@subscribe_api.resource('/subscribe/room/<int:room_id>')
class SubscribeModify(Resource):

    def delete(self, room_id):
        room = LiveTVRoom.query.get(room_id)
        if not room:
            return {'message': '找不到对应的房间记录，请检查ID是否正确'}, 400
        else:
            g.user.rooms.remove(room)
            db.session.add(g.user)
            db.session.commit()
        return {}
