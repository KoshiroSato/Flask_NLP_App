#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gc
import logging
from flask import Flask, render_template, request, abort, Response 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required
from lib.logger import app_logger
from lib.predict import Predict_Handler
from lib.mt5_model import define_mt5_model
from lib.bert_model import define_bert_model
from lib.user import build_checkDict, define_users
from lib.utils import get_dt_now_jst_aware, read_txt, read_yaml

# app init
app_conf = read_yaml('app_config.yml')
secretkey = read_yaml('secretkey.yml')
app = Flask(__name__)
app.config['DEBUG'] = app_conf['debug']
app.config['THREADED'] = app_conf['threaded']
login_manager = LoginManager()
login_manager.init_app(app)
app = app_logger(app)
app.config['SECRET_KEY'] = secretkey['secret_key']
users = define_users()
user_check = build_checkDict()
if not app_conf['debug']:
    app.logger.setLevel(logging.INFO)
    
# add SQLAlchemy config and SQLAlchemy init
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app_conf['db_path'] + app_conf['db_name']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# db init
class LoginUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(128), nullable=False)
    login_time = db.Column(db.String(32), nullable=False)

if app_conf['db_name'] not in os.listdir(app_conf['db_path']):
    db.create_all()

# ml model init
mt5_model_0 = define_mt5_model('headlines_generation')
mt5_model_1 = define_mt5_model('easy_japanese')
bert_models, bert_tokenizer = define_bert_model()


@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        entered_user_name = request.form['username']
        entered_password = request.form['password']
        if entered_user_name in user_check and entered_password == user_check[entered_user_name]['password']:
            user_id = user_check[entered_user_name]['id']
            user_name = entered_user_name
            login_user(users.get(user_id))
            # ログインユーザー情報をテーブルに追加
            login_time = get_dt_now_jst_aware()
            user_table = LoginUsers(
                user_id=user_id, 
                user_name=user_name,
                login_time=login_time
                )
            db.session.add(user_table)
            db.session.commit()
            return render_template('form.html')
        else:
            return abort(401)
    else:
        return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return Response(
        '''
        logout success!<br />
        <a href="/">login</a>
        '''
        )


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/result', methods=['POST'])
def result():
    input_text = request.form['input_text']
    ml_task = request.form['mltask_tab']
    submit_info = request.form['submit_btn']

    # サンプルデータの入力が選択されたら、input_textを更新
    if submit_info == 'sample data submit':
        if ml_task == 'headlines_generation':
            input_text = read_txt(app_conf['head_gen_sample_path'])
        elif ml_task == 'easy_japanese':
            input_text = read_txt(app_conf['easy_ja_sample_path'])
        elif ml_task == 'grammer_correction':
            input_text = read_txt(app_conf['gram_corr_sample_path'])
            
    predict_handler = Predict_Handler(mt5_model_0, mt5_model_1, bert_models, bert_tokenizer, ml_task)
    pred = predict_handler.predict(input_text)
    del predict_handler
    gc.collect()

    if ml_task == 'headlines_generation':
        ml_task = '記事タイトル生成'
        check_values = ['checked', None, None]
    elif ml_task == 'easy_japanese':
        ml_task = 'やさしい日本語'
        check_values = [None, 'checked', None]
    elif ml_task == 'grammer_correction':
        ml_task = '文章校正'
        check_values = [None, None, 'checked']

    return render_template('result.html', input_text=input_text, pred=pred, ml_task=ml_task, check_values=check_values)