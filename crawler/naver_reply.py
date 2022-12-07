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

  url = f"https://m.place.naver.com/restaurant/{fname.split('.')[0]}/review/visitor?reviewSort=recent"
  try:
    driver.get(url)
  except:
    print('failed: ' + fname)
    pass
  time.sleep(4)

  try:
    more_reply_button = driver.find_element(By.CSS_SELECTOR, 'div.place_section.lcndr a.fvwqf') # 댓글 더보기
    max_cnt = 0
    while more_reply_button and max_cnt < 100:
      more_reply_button.click()
      time.sleep(1)
      more_reply_button = driver.find_element(By.CSS_SELECTOR, 'div.place_section.lcndr a.fvwqf') # 댓글 더보기
      max_cnt += 1
  except Exception as e:
    pass

  try:
    more_content_buttons = driver.find_elements(By.CSS_SELECTOR, 'li.YeINN span.rvCSr') # 내용 더보기
    while more_content_buttons:
      for b in more_content_buttons:
        b.click()
        time.sleep(1)
      more_content_buttons = driver.find_elements(By.CSS_SELECTOR, 'li.YeINN span.rvCSr') # 내용 더보기
  except Exception as e:
    pass
  
  replies = []
  try:
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.place_section_content li.YeINN') # 댓글들
  except Exception as e:
    print('failed: ' + fname)
    return
  
  for el in elements:
    reply = ''
    score = -1
    
    try:
      reply = el.find_element(By.CSS_SELECTOR, 'span.zPfVt').text
    except:
      pass

    try:
      score = int(el.find_element(By.CSS_SELECTOR, 'span.P1zUJ.HNG_1 > em').text)
    except:
      pass
    
    replies.append({'reply': reply, 'score': score})

  with open('result/naver_reply/' + fname, 'w', encoding='utf-8') as fp:
    item['naver_pid'] = fname.split('.')[0]
    item['kakao_pid'] = item['pid']
    del item['pid']

    item['naver_reply'] = replies
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
  json_files = glob.glob('result/kakao/*.json')
  prev_files = glob.glob('result/naver_reply/*.json')

  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  start_time = time.time()
  for i, json_file in enumerate(json_files):
    result_file = json_file.replace('kakao', 'naver_reply')
    if result_file in prev_files:
      print('already processed: ' + json_file.split('/')[-1])
      continue

    with open(json_file, 'r', encoding='utf-8') as fp:
      data = json.load(fp)
      crawl(data, json_file.split('/')[-1])
    
    if i % 100 == 0:
      print(f'---- {i} ----')

  print('{:.2f}sec'.format(time.time() - start_time))