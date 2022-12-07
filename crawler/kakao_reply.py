import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import cssselect
import re
import time

webdriver_options = Options()
user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"
webdriver_options.add_argument('user-agent=' + user_agent)
webdriver_options.add_argument("incognito")
webdriver_options.add_argument('--blink-settings=imagesEnabled=false')
# webdriver_options.add_argument('headless')
driver = webdriver.Chrome(options=webdriver_options)
def crawl(item, fname):
  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
  }

  url = f"https://place.map.kakao.com/{item['kakao_pid']}"
  driver.get(url)
  time.sleep(4)

  try:
    more_reply_button = driver.find_element(By.CSS_SELECTOR, 'div.cont_grade a.link_more:not(.link_unfold)') # 댓글 더보기
    try:
      floating_button = driver.find_element(By.CSS_SELECTOR, 'div.floating_bnr a.btn_close') # 플로팅 버튼
      floating_button.click()
    except:
      pass

    while more_reply_button:
      more_reply_button.click()
      time.sleep(1)
      more_reply_button = driver.find_element(By.CSS_SELECTOR, 'div.cont_grade a.link_more:not(.link_unfold)')  # 댓글 더보기

      try:
        floating_button = driver.find_element(By.CSS_SELECTOR, 'div.floating_bnr a.btn_close') # 플로팅 버튼
        floating_button.click()
      except:
        pass

  except Exception as e:
    pass

  try:
    more_content_buttons = driver.find_elements(By.CSS_SELECTOR, 'p.txt_fold button.btn_fold') # 내용 더보기
    while more_content_buttons:
      for b in more_content_buttons:
        b.click()
        time.sleep(1)
      more_content_buttons = driver.find_elements(By.CSS_SELECTOR, 'p.txt_fold button.btn_fold') # 내용 더보기
  except Exception as e:
    pass
  
  replies = []
  try:
    elements = driver.find_elements(By.CSS_SELECTOR, 'ul.list_grade > li') # 댓글들
  except:
    print('failed: ' + fname)
    return
  
  for el in elements:
    reply = ''
    score = -1
    
    try:
      reply = el.find_element(By.CSS_SELECTOR, 'p.txt_comment > span').text
    except Exception as e:
      pass

    try:
      style = el.find_element(By.CSS_SELECTOR, 'span.inner_star').get_attribute('style')
      score = int(style.replace('width:', '').replace('%;', '')) / 20
    except Exception as e:
      pass
    
    replies.append({'reply': reply, 'score': score})
  with open('result/kakao_reply/' + fname, 'w', encoding='utf-8') as fp:
    item['kakao_reply'] = replies
    json.dump(item, fp, ensure_ascii=False)
  print('success: ' + fname)
    

import requests
import json
import multiprocessing
import time
import random
import pandas as pd
import numpy as np
import glob

if __name__ == '__main__':
  json_files = glob.glob('result/naver_reply/*.json')
  prev_files = glob.glob('result/kakao_reply/*.json')

  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  start_time = time.time()
  for i, json_file in enumerate(json_files):
    result_file = json_file.replace('naver', 'kakao')
    if result_file in prev_files:
      print('already processed: ' + json_file.split('/')[-1])
      continue

    with open(json_file, 'r', encoding='utf-8') as fp:
      data = json.load(fp)
      crawl(data, json_file.split('/')[-1])
    
    if i % 100 == 0:
      print(f'---- {i} ----')

  print('{:.2f}sec'.format(time.time() - start_time))