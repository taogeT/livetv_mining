#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from app import create_app, celery

import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
