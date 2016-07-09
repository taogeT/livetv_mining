# -*- coding: UTF-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, FormField
from wtforms.validators import Length


class SearchSiteForm(Form):
    douyu = BooleanField(label='斗鱼', default=True)
    panda = BooleanField(label='熊猫', default=True)
    zhanqi = BooleanField(label='战旗', default=True)


class SearchRoomForm(Form):
    site_code = FormField(SearchSiteForm, label='站点')
    host_nickname = StringField(label='主播名', default='', validators=[Length(0, 64)])
    room_name = StringField(label='房间名', default='', validators=[Length(0, 128)])
    submit = SubmitField(label='搜索')
