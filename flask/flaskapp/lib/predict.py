#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.logger import model_io_logger
from lib.utils import text_preprocess, text_split
from lib.bert_model import bert_predict
from lib.mt5_model import mt5_post_processing


class Predict_Handler(object):
    def __init__(
        self, 
        mt5_model_0, 
        mt5_model_1, 
        bert_models, 
        bert_tokenizer, 
        ml_task
        ):
        self.mt5_model_0 = mt5_model_0
        self.mt5_model_1 = mt5_model_1
        self.bert_models = bert_models
        self.bert_tokenizer = bert_tokenizer
        self.ml_task = ml_task

    def predict(self, input_text):
        input_text = text_preprocess(input_text)
        io_logger = model_io_logger(self.ml_task)
        io_logger.info(input_text)

        if self.ml_task == 'headlines_generation':
            preds = self.mt5_model_0.predict([input_text])
            pred = preds[0]
            pred = mt5_post_processing(pred, self.bert_tokenizer)

        elif self.ml_task == 'easy_japanese':
            input_texts = text_split(input_text, self.ml_task)
            preds = self.mt5_model_1.predict(input_texts)
            pred = ''.join(preds)
            pred = mt5_post_processing(pred, self.bert_tokenizer)

        elif self.ml_task == 'grammer_correction':
            input_texts = text_split(input_text, self.ml_task)
            preds = [
                bert_predict(inp, self.bert_tokenizer, self.bert_models) for inp in input_texts
                ]
            pred = ''.join(preds)
        io_logger.info(pred)
        return pred