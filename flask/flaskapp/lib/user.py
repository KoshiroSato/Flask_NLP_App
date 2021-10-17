#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from flask_login import UserMixin
from lib.utils import read_yaml


class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password


def define_users():
    user = read_yaml('user.yml')
    return {1: User(user['user_id'], user['user_name'], user['password'])}


def build_checkDict():
    users = define_users()
    nested_dict = lambda: defaultdict(nested_dict)
    user_check = nested_dict()
    for i in users.values():
        user_check[i.name]['password'] = i.password
        user_check[i.name]['id'] = i.id
    return user_check