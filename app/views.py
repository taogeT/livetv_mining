# -*- coding: UTF-8 -*-
from flask import render_template
from markdown import markdown

import codecs


def about():
    """ 关于 """
    with codecs.open('README.md', 'r', encoding='utf-8') as mdf:
        mdhtml = markdown(mdf.read())
    return render_template('about.html', mdhtml=mdhtml)
