#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from app import create_app, celery
from app.tasks import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
