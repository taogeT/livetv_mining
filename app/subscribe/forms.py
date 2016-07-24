# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import Length, Required


class SubscribeAddForm(Form):
    roomurl = StringField(label='房间URL', default='', validators=[Required()])
    submit = SubmitField(label='订阅')


class SubscribeCancelForm(Form):
    roomid = HiddenField(label='房间ID', default='', validators=[Required()])
    submit = SubmitField(label='取消订阅')

