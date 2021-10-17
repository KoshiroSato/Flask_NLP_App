#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.utils import read_yaml

app_conf = read_yaml('app_config.yml')

wsgi_app = 'app:app'
bind = app_conf['bind']
workers = app_conf['workers']
timeout = app_conf['timeout']