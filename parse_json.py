import json
from pprint import pprint



def read_json(name_json_file:str):
    # Открываем и читаем JSON-файл
    with open(name_json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


if __name__ == '__main__':
    data_videos = read_json(name_json_file='videos.json')
    data_videos = data_videos['videos']
    for video in data_videos:
        print(video['creator_id'])