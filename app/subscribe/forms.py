# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Required


class SubscribeRoomForm(Form):
    roomurl = StringField(label='房间URL', default='', validators=[Required()])
    submit = SubmitField(label='订阅')
