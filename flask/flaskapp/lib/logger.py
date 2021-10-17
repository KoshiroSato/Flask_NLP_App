#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler


def app_logger(app):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s ''[in %(pathname)s:%(lineno)d]'
        )
    debug_file_handler = RotatingFileHandler(
        '/temp/flask_simple_app/flask/flaskapp/logs/debug.log', 
        maxBytes=100000, 
        backupCount=10
        )
    debug_file_handler.setLevel(logging.INFO)
    debug_file_handler.setFormatter(formatter)
    debug_werkzeug_logger = logging.getLogger('werkzeug')
    debug_werkzeug_logger.addHandler(debug_file_handler)
    app.logger.addHandler(debug_werkzeug_logger)
    error_file_handler = RotatingFileHandler(
        '/temp/flask_simple_app/flask/flaskapp/logs/error.log', 
        maxBytes=100000, 
        backupCount=10
        )    
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    error_werkzeug_logger = logging.getLogger('werkzeug')
    error_werkzeug_logger.addHandler(debug_file_handler)
    app.logger.addHandler(error_werkzeug_logger)
    return app


def model_io_logger(ml_task):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler1 = logging.StreamHandler()
    handler1.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s ''[in %(pathname)s:%(lineno)d]')
        )
    handler2 = logging.FileHandler(
        filename=f'/temp/flask_simple_app/flask/flaskapp/logs/{ml_task}_model_io.log'
        )
    handler2.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s ''[in %(pathname)s:%(lineno)d]')
        )
    logger.addHandler(handler1)
    logger.addHandler(handler2)
    return logger