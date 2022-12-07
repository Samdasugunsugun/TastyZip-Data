def crawl(row):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
  }

  url = f"https://m.map.naver.com/search2/searchMore.naver?query={row['naver_keyword']}&sm=clk&style=v5&page=1&displayCount=75&type=SITE_1"
  resp = requests.get(url, headers=headers)
  while str(resp.status_code) != '200':
    print('failed: ' + str(resp.status_code))
    time.sleep(3600) # 1시간 wait
    resp = requests.get(url, headers=headers)
  root = json.loads(resp.text)

  desc_url = ''

  try:
    places = root['result']['site']['list']
    for p in places:
      addr = p['roadAddress']
      pid = p['id'].replace('s', '')

      if row['addr'] in addr:
        desc_url = pid
        break
  except:
    pass
  
  if desc_url != '':
    with open('result/naver/' + desc_url + '.json', 'w', encoding='utf-8') as fp:
      d = {
        'name': row['name'],
        'cat1': row['cate_1'],
        'cat2': row['cate_2'],
        'cat3': row['cate_3'],
        'addr': row['addr'],
        'lon': row['lon'],
        'lat': row['lat'],
        'keyword': row['naver_keyword']
      }
      json.dump(d, fp, ensure_ascii=False)
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
  # csv_files = glob.glob('data/*.csv')
  csv_files = glob.glob('data/seoul.csv')
  total_df = pd.DataFrame()

  for csv in csv_files:
    df = pd.read_csv(csv, sep=',') 

    # 음식점 데이터만 쓸 겁니다
    df = df.loc[(df['상권업종대분류명'] == '음식') & (df['시군구명'] == '성북구')]  

    # 다음과 같은 칼럼만 있으면 됩니다
    df = df[['상호명', '상권업종중분류명', '상권업종소분류명', '표준산업분류명', '행정동명', '도로명주소', '위도', '경도']]

    # 칼럼명 단순화

    df.columns = ['name',  # 상호명
                  'cate_1',  # 중분류명
                  'cate_2',  # 소분류명
                  'cate_3',  # 표준산업분류명
                  'dong', # 행정동명
                  'addr',  # 도로명주소
                  'lon',  # 위도
                  'lat'  # 경도
                  ]

    total_df = pd.concat([total_df, df])

  total_df['naver_keyword'] = total_df['dong'] + "%20" + total_df['name']  # "%20"는 띄어쓰기를 의미합니다.
  total_df['naver_map_url'] = ''
  print('file read complete, rows: ' + str(total_df.shape[0]))


  # 본격적으로 가게 상세페이지의 URL을 가져옵시다
  start_time = time.time()
  for i, keyword in enumerate(total_df['naver_keyword'].tolist()):
    crawl(total_df.iloc[i])
    time.sleep(random.uniform(4.0, 6.0))
    if i % 100 == 0:
      print(f'---- {i} ----')

  print('{:.2f}sec'.format(time.time() - start_time))