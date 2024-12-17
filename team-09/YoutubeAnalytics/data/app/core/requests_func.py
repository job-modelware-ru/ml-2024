from data.app.config.quota_size import *
from data.app.config.requests_types import *
from data.app.core.youtube import Youtube
from math import ceil

import json

from data.app.db.db import DataBase


def get_channel_by_id(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    channel = youtube.get_channel(data["id"])

    db.store_channel(channel, data["id"])

    playlist_id = data["id"][:1] + 'U' + data["id"][2:]

    db.add_scraper_request(GET_VIDEOS_BY_CHANNEL_ID, ceil(float(channel["videoCount"]) / 50), json.dumps({
            "id": playlist_id,
            "pageToken": None
        }), user_id)


def get_channel_by_url(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    channel = youtube.get_channel_by_url(data["url"])

    db.store_channel(channel, channel["id"])

    playlist_id = channel["id"][:1] + 'U' + channel["id"][2:]

    db.add_scraper_request(GET_VIDEOS_BY_CHANNEL_ID, ceil(float(channel["videoCount"]) / 50), json.dumps({
            "id": playlist_id,
            "pageToken": None
        }), user_id)


def get_channel_by_video_id(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    channel = youtube.get_channel_by_video_id(data["id"])

    db.store_channel(channel, channel["id"])

    playlist_id = channel["id"][:1] + 'U' + channel["id"][2:]

    db.add_scraper_request(GET_VIDEOS_BY_CHANNEL_ID, ceil(float(channel["videoCount"]) / 50), json.dumps({
            "id": playlist_id,
            "pageToken": None
        }), user_id)


def get_videos_by_channel_id(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    next_page_token, videos_ids = youtube.get_videos(
        data["id"], data["pageToken"])

    for video_id in videos_ids:
        db.add_scraper_request(GET_VIDEO_BY_ID, 1, json.dumps({
            "id": video_id,
            "pageToken": None
        }), user_id)

    data["pageToken"] = next_page_token


def get_video_by_id(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    video = youtube.get_video(data["id"])

    if video is None:
        return

    db.store_video(video, data["id"])

    if "commentCount" in video and video["commentCount"] != None:
        tasks_left = ceil(float(video["commentCount"]) / 100)
        if tasks_left > 0:
            db.add_scraper_request(GET_COMMENTS_BY_VIDEO_ID, tasks_left, json.dumps({
                    "id": data["id"],
                    "pageToken": None
                }), user_id)


def get_comments_by_video_id(youtube: Youtube, data: dict, db: DataBase, user_id) -> None:
    next_page_token, comments = youtube.get_comments(
        data["id"], data["pageToken"])

    db.store_comments(comments)

    data["pageToken"] = next_page_token


requests_func = {
    GET_CHANNEL_BY_ID: get_channel_by_id,
    GET_VIDEOS_BY_CHANNEL_ID: get_videos_by_channel_id,
    GET_VIDEO_BY_ID: get_video_by_id,
    GET_COMMENTS_BY_VIDEO_ID: get_comments_by_video_id,
    GET_CHANNEL_BY_URL: get_channel_by_url,
    GET_CHANNEL_BY_VIDEO_ID: get_channel_by_video_id,
}

requests_quota_size = {
    GET_CHANNEL_BY_ID: LIST_REQUEST,
    GET_VIDEOS_BY_CHANNEL_ID: LIST_REQUEST,
    GET_VIDEO_BY_ID: LIST_REQUEST,
    GET_COMMENTS_BY_VIDEO_ID: LIST_REQUEST,
    GET_CHANNEL_BY_URL: SEARCH_REQUEST + LIST_REQUEST,
    GET_CHANNEL_BY_VIDEO_ID: LIST_REQUEST + LIST_REQUEST
}
