import unittest

from emotion_analisis.analyser import Analyser
from metrics.loader import Loader
from requests_func import *
from db.db import DataBase


class TestLoading(unittest.TestCase):
    def test_time_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_time_analisis(data, db)
        db.close_connection()

    def test_lang_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        analyser = Analyser()
        comments = loader.get_all_comments(ch_id, v_id)
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_lang_analisis(data, db, analyser)
        db.close_connection()

    def test_emotion_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        analyser = Analyser()
        comments = loader.get_all_comments(ch_id, v_id)
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_emotion_analisis(data, db, analyser)
        db.close_connection()

    def test_word_map_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        analyser = Analyser()
        comments = loader.get_all_comments(ch_id, v_id)
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_word_map(data, db, analyser)
        db.close_connection()

    def test_likes_vs_replies_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_likes_vs_replies_analisis(data, db)
        db.close_connection()

    def test_neq_pos_analisis(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        analyser = Analyser()
        data = {
            'comments': comments,
            'videoId': v_id,
            'channelId': ch_id
        }
        db = DataBase()
        db.create_connection()
        get_neq_pos_analisis(data, db, analyser=analyser)
        db.close_connection()