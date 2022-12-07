import requests
import json
from lxml import html
import cssselect
import re
import time


def crawl(item, fname):
  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
  }

  url = f"https://m.map.kakao.com/actions/searchView?q={item['keyword']}"
  resp = requests.get(url, headers=headers)
  while str(resp.status_code) != '200':
    print('failed: ' + str(resp.status_code))
    time.sleep(3600) # 1시간 wait
    resp = requests.get(url, headers=headers)
  root = html.fromstring(resp.text)

  desc_url = ''
  
  try:
    elements = root.cssselect('#placeList > li.search_item.base')
    for el in elements:
      addr = re.sub(' +', ' ', el.cssselect('.txt_g')[0].text)
      pid = el.attrib['data-id']
      removed = ' '.join(item['addr'].split(' ')[1:])
      if removed in addr:
        desc_url = pid
        break

  except:
    pass 

  if desc_url != '':
    with open('result/kakao/' + fname, 'w', encoding='utf-8') as fp:
      item['pid'] = desc_url
      json.dump(item, fp, ensure_ascii=False)
    print('success: ' + desc_url)
  else:
    print('failed: ' + str(resp.status_code))
    

import requests
import json
import multiprocessing
import time
import random
import pandas as pd
import numpy as np
import glob

if __name__ == '__main__':
  json_files = glob.glob('result/naver/*.json')

  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  start_time = time.time()
  for i, json_file in enumerate(json_files):
    with open(json_file, 'r', encoding='utf-8') as fp:
      data = json.load(fp)
      crawl(data, json_file.split('/')[-1])
    
    time.sleep(random.uniform(4.0, 6.0))
    if i % 1000 == 0:
      print(f'---- {i} ----')

  print('{:.2f}sec'.format(time.time() - start_time))