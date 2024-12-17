import json
import time

from db.config import *
from db.db import DataBase
from emotion_analisis.analyser import Analyser
from metrics.loader import Loader
from requests_func import requests_func
from sshtunnel import SSHTunnelForwarder


def check_video(video_id, db: DataBase) -> bool:
    return db.is_video_exists(video_id)


def check_channel(channel_id: str, db: DataBase) -> bool:
    return db.is_channel_exists(channel_id)


def process(db: DataBase, port: int):
    analyser = Analyser()
    loader = Loader(db=db)
    while True:
        request = db.get_scraper_request(7, 14)
        if not request:
            continue
        data = json.loads(request[4])
        video_id = data.get('video_id')
        channel_id = data.get('channel_id')
        if video_id and check_video(video_id, db):
            loader.load_video(video_id)
        if channel_id and check_channel(channel_id, db):
            loader.load_channel(channel_id)
        db.pre_update_request(request)
        data = {
            'channelId': channel_id,
            'videoId': video_id,
            'comments': loader.get_data_comments(channel_id, video_id),
            'video_info': loader.get_video_info(video_id, channel_id),
            'userId': request[5]
        }
        print("req", request)
        start_time = time.time()
        requests_func[request[1]](data, db, analyser)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Elapsed time: ', elapsed_time)
        db.update_scraper_request(request[0], request[2] - 1)


if __name__ == "__main__":
    print("Analyser started")
    port = 22
    if ssh_connection:
        server = SSHTunnelForwarder(ssh_ip, ssh_username=ssh_username,
                                    ssh_password=ssh_password, remote_bind_address=(db_ip, db_port))

        server.start()

        port = server.local_bind_port
    db = DataBase()
    db.create_connection(port)
    while True:
        try:
            process(db, port)
        except:
            continue
    db.close_connection()
