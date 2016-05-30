# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length


class SearchRoomForm(Form):
    site_name = SelectField('站点', validators=[Length(0, 64)])
    boardcaster = StringField('主播名', validators=[Length(0, 64)])
    room_name = StringField('房间名', validators=[Length(0, 128)])
    only_active = BooleanField('正在直播', default=True)
    submit = SubmitField('搜索')
