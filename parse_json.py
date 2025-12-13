import json

from faker import Faker

from src.database.method_db import create_object
from src.database.models import Creators, Videos, VideoSnapshots
from sqlalchemy.orm import configure_mappers

# Это нужно, чтобы SQLAlchemy "увидел" все relationship
configure_mappers()


fake = Faker('ru_RU')


def create_creator_in_db(user_id):
    create_object(
        model=Creators,
        creator_id=user_id,
        name=fake.name(),
        date_registration=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=None)
    )



def read_json(name_json_file:str):
    # Открываем и читаем JSON-файл
    with open(name_json_file, 'r', encoding='utf-8') as file:
        return json.load(file)


if __name__ == '__main__':
    data_videos = read_json(name_json_file='videos.json')
    data_videos = data_videos['videos']
    for video in data_videos:
        for snapshot in video['snapshots']:
            pass
            # create_object(
            #     model=VideoSnapshots,
            #     id=snapshot['id'],
            #     video_id=snapshot['video_id'],
            #     views_count=snapshot['views_count'],
            #     likes_count=snapshot['likes_count'],
            #     reports_count=snapshot['reports_count'],
            #     comments_count=snapshot['comments_count'],
            #     delta_views_count=snapshot['delta_views_count'],
            #     delta_likes_count=snapshot['delta_likes_count'],
            #     delta_reports_count=snapshot['delta_reports_count'],
            #     delta_comments_count=snapshot['delta_comments_count'],
            #     created_at=snapshot['created_at'],
            #     updated_at=snapshot['updated_at']
            # )