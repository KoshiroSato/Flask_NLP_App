#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import datetime
import mojimoji


def get_dt_now_jst_aware():
    dt_now_jst_aware = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
        )
    dt_now_jst_aware = dt_now_jst_aware.strftime('%Y-%m-%d %H:%M:%S')
    return dt_now_jst_aware


def read_txt(file_path):
    try:
        with open(file_path) as f:
            text = f.read()
    except FileNotFoundError:
        text = 'FileNotFound'
    return text


def read_yaml(file_name):
    with open(f'/temp/flask_simple_app/flask/flaskapp/yaml/{file_name}', 'r') as yml:
        config = yaml.load(yml, Loader=yaml.FullLoader)
    return config


def text_preprocess(text):
    text = ''.join(text.split())
    text = mojimoji.han_to_zen(text, ascii=False, digit=False)
    text = mojimoji.zen_to_han(text, kana=False)
    return text


def text_split(text, ml_task):
    '''
    first_time_split: テキストを句点で分割
    second_time_split: タスクに応じて条件付きで、さらにテキストを読点で分割
    '''
    def first_time_split(text, delimiter='。'):
        texts = text.split(delimiter)[:-1]
        # splitで句点が消えるので、追加
        texts = [text+delimiter for text in texts]
        return texts

    def second_time_split(texts, delimiter='、', threshold=None):
        results = []
        for text in texts:
            if threshold is not None:
                if len(text) >= threshold:
                    split_texts = text.split(delimiter)
                    # splitで読点が消えるので、追加
                    for i in range(len(split_texts) - 1):
                        split_texts[i] += delimiter
                    results.extend(split_texts)
                # 閾値以下の文字数のテキストには適用しない
                else:
                    results.append(text)
            # 閾値をセットしていない場合は、全データに適用する
            else:
                split_texts = text.split(delimiter)
                # splitで読点が消えるので、追加
                for i in range(len(split_texts) - 1):
                    split_texts[i] += delimiter
                results.extend(split_texts)
        return results

    if ml_task == 'grammer_correction':
        grammer_cfg = read_yaml('bert_mlm_pred_params.yml')
        texts = first_time_split(text)
        # モデルの学習データの平均文字数に合わせて、閾値をセットする
        results = second_time_split(texts, threshold=grammer_cfg['second_split_threshold'])
    
    elif ml_task == 'easy_japanese':
        results = first_time_split(text)

    return results