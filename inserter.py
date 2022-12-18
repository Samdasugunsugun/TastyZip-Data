import glob
import time
import json

if __name__ == '__main__':
  json_files = glob.glob('result/final/*.json')
  start_time = time.time()

  keywords = set()
  restaurants = []
  reviews = []

  for i, json_file in enumerate(json_files):
    temp_reviews = []
    with open(json_file, 'r', encoding='utf-8') as fp:
      data = json.load(fp)
      restaurants.append({
        'id': i+1,
        'name': data['name'],
        'category': data['cat2'],
        'address': data['addr'],
        'lat': data['lon'],
        'lon': data['lat'],
        'score': 0.0
      })
      restaurant_score = 0

      for reply in data['naver_reply']:
        total_score = reply['poscore']
        if reply['score'] != -1:
          total_score = total_score * 0.5 + reply['score'] * 0.1

        temp_reviews.append({
          'id': len(reviews) + len(temp_reviews)+ 1,
          'restaurant_id': i+1,
          'content': reply['reply'].replace('\0', '').replace("'", r"\'"),
          'score': total_score * 5,
          'keywords': reply['keywords']
        })
        restaurant_score += total_score * 5
        keywords.update(reply['keywords'])

      for reply in data['kakao_reply']:
        total_score = reply['poscore']
        if reply['score'] != -1:
          total_score = total_score * 0.5 + reply['score'] * 0.1


        temp_reviews.append({
          'id': len(reviews) + len(temp_reviews) + 1,
          'restaurant_id': i + 1,
          'content': reply['reply'].replace('\0', '').replace("'", r"\'"),
          'score': total_score * 5,
          'keywords': reply['keywords']
        })
        restaurant_score += total_score * 5
        keywords.update(reply['keywords'])

      reviews.extend(temp_reviews)
      restaurants[-1]['score'] = restaurant_score / len(temp_reviews) if len(temp_reviews) != 0 else 0.0

    if i % 100 == 0:
      print(f'---- {i} ----')

  keywords = list(keywords)
  keywords = [keyword for keyword in keywords if '\n' not in keyword]
  k2i = {keyword: idx for idx, keyword in enumerate(keywords)}
  connects = []

  for review in reviews:
    for keyword in review['keywords']:
      if keyword not in k2i:
        continue

      connects.append({
        'id': len(connects) + 1,
        'review_id': review['id'],
        'keyword_id': k2i[keyword]
      })
  with open('init.sql', 'w', encoding='utf-8') as fp:
    for restaurant in restaurants:
      fp.write(f"insert ignore into restaurant(restaurant_id, name, category, address, lat, lon, score) values({restaurant['id']}, '{restaurant['name']}', '{restaurant['category']}', '{restaurant['address']}', {restaurant['lat']}, {restaurant['lon']}, {restaurant['score']});\n")

    for idx, keyword in enumerate(keywords):
      fp.write(f"insert ignore into keyword(keyword_id, keyword) values({idx+1}, '{keyword}');\n")

    for review in reviews:
      fp.write(f"insert ignore into review(review_id, restaurant_id, content, score) values({review['id']}, {review['restaurant_id']}, '{review['content']}', {review['score']});\n")

    for idx in range(0, len(connects), 500):
      query = f"insert ignore into connect(connect_id, review_id, keyword_id) values"
      for i in range(0, 500):
        if idx+i >= len(connects): break
        query += f"({connects[idx+i]['id']}, {connects[idx+i]['review_id']}, {connects[idx+i]['keyword_id']})"
        if i != 499 and idx+i+1 < len(connects):
          query += ','
      fp.write(f"{query};\n")
  print('{:.2f}sec'.format(time.time() - start_time))