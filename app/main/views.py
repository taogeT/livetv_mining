# -*- coding: UTF-8 -*-
from flask import render_template
from markdown import markdown

from . import main

import codecs


@main.route('/')
@main.route('/index')
def index():
    """ 网站基本介绍 """
    return render_template('index.html')


@main.route('/about')
def about():
    """ 关于 """
    with codecs.open('ABOUT.md', 'r', encoding='utf-8') as mdf:
        mdhtml = markdown(mdf.read())
    return render_template('about.html', mdhtml=mdhtml)
