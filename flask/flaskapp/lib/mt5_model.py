#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import torch
from simpletransformers.t5 import T5Model
from lib.utils import read_yaml


def define_mt5_model(ml_task):
    if ml_task == 'headlines_generation':
        yaml_path = 'headlines_mt5_pred_params.yml'
        model_path = '/temp/flask_simple_app/flask/flaskapp/ml_model/mt5/headlines_generation'
    elif ml_task == 'easy_japanese':
        yaml_path = 'easy_mt5_pred_params.yml'
        model_path = '/temp/flask_simple_app/flask/flaskapp/ml_model/mt5/easy_japanese'

    warnings.simplefilter('ignore')
    pred_params = read_yaml(yaml_path)
    
    device = torch.cuda.is_available()
    model = T5Model('mt5', model_path, args=pred_params, use_cuda=device)
    return model


def mt5_post_processing(text, tokenizer):
    # BERTのトークナイザーを共用する
    words = tokenizer.word_tokenizer.tokenize(text)
    # 文章内のrepetition wordを除去
    post_words = ['']
    for word in words:
        if not word == post_words[-1]:
            post_words.append(word)
    post_pred = ''.join(post_words)
    return post_pred