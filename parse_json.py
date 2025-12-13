import json
from pprint import pprint



# Открываем и читаем JSON-файл
with open('videos.json', 'r', encoding='utf-8') as file:
    data_videos = json.load(file)

# Получаем целиком все данные
data_videos = data_videos['videos']


