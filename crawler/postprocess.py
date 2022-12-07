import json
import glob
import time

from konlpy.tag import Okt
okt = Okt()
alist = ('Noun', 'Modifier', 'Adjective', 'Foreign')

import tensorflow as tf
import torch
import pandas as pd
import numpy as np
from transformers import BertForSequenceClassification
from transformers import BertTokenizer
from keras_preprocessing.sequence import pad_sequences

device = torch.device("cpu")
model = BertForSequenceClassification.from_pretrained("bert-base-multilingual-cased", num_labels=2)
model.load_state_dict(torch.load('../model.pt', map_location=torch.device('cpu')))
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', do_lower_case=False)

def add_keywords(reply):
  pos = okt.pos(reply['reply'], norm=True, stem=True)
  keywords = []

  for p in pos:
    if len(p) > 1 and p[1] in alist and p[0] != '\n':
      keywords.append(p[0])

  reply['keywords'] = keywords
  return reply

# 입력 데이터 변환
def convert_input_data(sentences):

    # BERT의 토크나이저로 문장을 토큰으로 분리
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

    # 입력 토큰의 최대 시퀀스 길이
    MAX_LEN = 128

    # 토큰을 숫자 인덱스로 변환
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]
    
    # 문장을 MAX_LEN 길이에 맞게 자르고, 모자란 부분을 패딩 0으로 채움
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # 어텐션 마스크 초기화
    attention_masks = []

    # 어텐션 마스크를 패딩이 아니면 1, 패딩이면 0으로 설정
    # 패딩 부분은 BERT 모델에서 어텐션을 수행하지 않아 속도 향상
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask)

    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)

    return inputs, masks

# 문장 테스트
def test_sentences(sentences):

    # 평가모드로 변경
    model.eval()

    # 문장을 입력 데이터로 변환
    inputs, masks = convert_input_data(sentences)

    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
            
    # 그래디언트 계산 안함
    with torch.no_grad():     
        # Forward 수행
        outputs = model(b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask)

    # 로스 구함
    logits = outputs[0]

    # CPU로 데이터 이동
    logits = logits.detach().cpu().numpy()

    return logits

def add_positive_score(reply):
  logits = test_sentences([reply['reply']])
  predictions = tf.nn.softmax(logits)
  reply['poscore'] = float(predictions[0][1])
  return reply

if __name__ == '__main__':
  json_files = glob.glob('result/kakao_reply/*.json')
  start_time = time.time()
  
  for i, json_file in enumerate(json_files):
    with open(json_file, 'r', encoding='utf-8') as fp:
      new_file = f"result/final/{json_file.split('/')[-1]}"
      data = json.load(fp)

      naver_reply = []
      kakao_reply = []
      
      for reply in data['naver_reply']:
        r = add_keywords(reply)
        naver_reply.append(add_positive_score(r))
        

      for reply in data['kakao_reply']:
        r = add_keywords(reply)
        kakao_reply.append(add_positive_score(r))
        
      data['naver_reply'] = naver_reply
      data['kakao_reply'] = kakao_reply

      with open(new_file, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False)

    if i % 100 == 0:
      print(f'---- {i} ----')
  print('{:.2f}sec'.format(time.time() - start_time))