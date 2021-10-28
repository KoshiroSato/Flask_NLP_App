#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import unicodedata
import torch
import pytorch_lightning as pl
from transformers import BertJapaneseTokenizer, BertForMaskedLM
from lib.utils import read_yaml

# reference: https://github.com/stockmarkteam/bert-book/blob/master/Chapter9.ipynb
class GrammerTokenizer(BertJapaneseTokenizer):
    def encode_plus_tagged(self, wrong_text, correct_text, max_length=128):
        encoding = self(
            wrong_text, 
            add_special_tokens=True,
            max_length=max_length, 
            padding='max_length', 
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        encoding_correct = self(
            correct_text,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        ) 
        encoding['labels'] = encoding_correct['input_ids'] 

        return encoding

    def encode_plus_untagged(self, text, max_length=None, return_tensors=None):
        tokens = [] 
        tokens_original = [] 
        words = self.word_tokenizer.tokenize(text)
        for word in words:
            tokens_word = self.subword_tokenizer.tokenize(word) 
            tokens.extend(tokens_word)
            if tokens_word[0] == '[UNK]': 
                tokens_original.append(word)
            else:
                tokens_original.extend([
                    token.replace('##','') for token in tokens_word
                ])

        position = 0
        spans = [] 
        for token in tokens_original:
            l = len(token)
            while 1:
                if token != text[position:position+l]:
                    position += 1
                else:
                    spans.append([position, position+l])
                    position += l
                    break

        input_ids = self.convert_tokens_to_ids(tokens) 
        encoding = self.prepare_for_model(
            input_ids, 
            max_length=max_length, 
            padding='max_length' if max_length else False, 
            truncation=True if max_length else False
        )
        sequence_length = len(encoding['input_ids'])
        spans = [[-1, -1]] + spans[:sequence_length-2] 
        spans = spans + [[-1, -1]] * ( sequence_length - len(spans) ) 

        if return_tensors == 'pt':
            encoding = { k: torch.tensor([v]) for k, v in encoding.items() }

        return encoding, spans

    def convert_bert_output_to_text(self, text, labels, spans):
        assert len(spans) == len(labels)

        labels = [label for label, span in zip(labels, spans) if span[0]!=-1]
        spans = [span for span in spans if span[0]!=-1]

        predicted_text = ''
        position = 0
        for label, span in zip(labels, spans):
            start, end = span
            if position != start: 
                predicted_text += text[position:start]
            predicted_token = self.convert_ids_to_tokens(label)
            predicted_token = predicted_token.replace('##', '')
            predicted_token = unicodedata.normalize(
                'NFKC', predicted_token
            ) 
            predicted_text += predicted_token
            position = end
        
        return predicted_text


class GrammerModel(pl.LightningModule):
    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name
        self.bert_mlm = BertForMaskedLM.from_pretrained(self.model_name)


def define_bert_model():
    warnings.simplefilter('ignore')
    pred_params = read_yaml('bert_mlm_pred_params.yml')
    tokenizer = GrammerTokenizer.from_pretrained(pred_params['model_name'])
    # kanji-conversion_model
    conversion_model = GrammerModel(pred_params['model_name']) 
    conversion_model.load_state_dict(torch.load(pred_params['ckpt_path_0'], map_location='cpu')['state_dict'])
    conversion_mlm = conversion_model.bert_mlm
    # substitution_model
    substitution_model = GrammerModel(pred_params['model_name'])
    substitution_model.load_state_dict(torch.load(pred_params['ckpt_path_1'], map_location='cpu')['state_dict'])
    substitution_mlm = substitution_model.bert_mlm
    return [conversion_mlm, substitution_mlm], tokenizer


def predict_with_post_processing(text, tokenizer, bert_model):
    encoding, spans = tokenizer.encode_plus_untagged(text, return_tensors='pt')
    encoding = {k: v for k, v in encoding.items()}
    with torch.no_grad():
        output = bert_model(**encoding)
        scores = output.logits
        labels_predicted = scores[0].argmax(-1).numpy().tolist()
    predict_text = tokenizer.convert_bert_output_to_text(text, labels_predicted, spans)
    # 文章内のrepetition wordを除去
    words = tokenizer.word_tokenizer.tokenize(predict_text)
    post_words = ['']
    for word in words:
        if not word == post_words[-1]:
            post_words.append(word)
    post_pred = ''.join(post_words)
    # '[SEP]','[PAD]'を除去
    post_pred = post_pred.replace('[SEP]', '')
    post_pred = post_pred.replace('[PAD]', '')
    return post_pred


def bert_predict(text, tokenizer, bert_models):
    # kanji-conversion_modelの推論結果を
    # substitution_modelへ入力し、推論させる
    for bert_model in bert_models:
        text = predict_with_post_processing(text, tokenizer, bert_model)
    predict_text = text
    return predict_text