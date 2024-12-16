import json
import logging
from datetime import date, datetime

# from db.config.collections_names import *
import psycopg2
from db.config import *


class DataBase:
    def __init__(self) -> None:
        self.__server = None
        self.__db_connection = None
        self.__db = None

    def create_connection(self, port) -> bool:
        self.__db_connection = psycopg2.connect(dbname=database_name, user=db_username, password=db_password,
                                                host=db_ip, port=port)
        self.__db = self.__db_connection.cursor()

        logging.info("Database connection created")

        return True

    def close_connection(self) -> None:
        if self.__db_connection:
            self.__db_connection.close()

        logging.info("Close db connection")

    def reset_api_quota(self) -> bool:
        today = date.today()

        self.__db.execute("select id from tb_api_keys where last_reset<%(date)s", {"date": today})
        result = self.__db.fetchall()

        if result is None:
            return False

        api_ids = result
        self.__db.executemany(
            "UPDATE tb_api_keys SET remaining_quota=%(quota)s, last_reset=%(date)s WHERE id = %(api_id)s",
            [{"quota": 10000, "date": today, "api_id": api_id} for api_id in api_ids])
        self.__db_connection.commit()

        return True

    def get_scraper_requests(self, min_type, max_type, num_requests) -> list:
        self.__db.execute("""select id, type_id, data, progress, user_id from tb_request where type_id<%(max_type)s 
                          and type_id>=%(min_type)s and progress>%(progress)s limit %(num_requests)s""",
                          {"min_type": min_type, "max_type": max_type, "num_requests": num_requests, "progress": 0})
        result = self.__db.fetchall()

        return result

    def get_available_api(self, min_quota_size) -> dict | None:
        self.__db.execute("select api_key, remaining_quota from tb_api_keys where remaining_quota>=%(min_quota_size)s",
                          {"min_quota_size": min_quota_size})
        result = self.__db.fetchone()

        return result and {"key": result[0], "quota": result[1]}

    def update_api_quota(self, key, quota_size) -> bool:
        self.__db.execute("update tb_api_keys set remaining_quota=%(quota)s WHERE api_key = %(key)s",
                          {"quota": quota_size, "key": key})
        self.__db_connection.commit()

        return True

    def update_scraper_request(self, request_id, request_progress):
        date_completion = None
        if request_progress <= 0:
            date_completion = datetime.today().isoformat()

        self.__db.execute(
            "update tb_request set progress=%(progress)s, date_completion=%(date_completion)s WHERE id = %(id)s",
            {"progress": request_progress, "id": request_id, "date_completion": date_completion})
        self.__db_connection.commit()

    def store_channel(self, channel: dict, channel_id: str) -> bool:
        self.__db.execute("""insert into tb_channel(country, description, published_at, subscriber_count, title, video_count, view_count, yt_id, custom_url) values 
                          (%(country)s, %(description)s, %(publishedAt)s, %(subscriber_count)s, 
                          %(title)s, %(video_count)s, %(view_count)s, %(yt_id)s, %(customUrl)s) ON CONFLICT (yt_id) DO NOTHING""",
                          {"country": channel["country"], "description": channel["description"],
                           "publishedAt": channel["publishedAt"], "subscriber_count": channel["subscriberCount"],
                           "title": channel["title"], "video_count": channel["videoCount"],
                           "view_count": channel["viewCount"], "yt_id": channel_id, "customUrl": channel["customUrl"]})
        self.__db_connection.commit()

        return True

    def add_scraper_request(self, type_id, progress, data, user_id):
        self.__db.execute("""insert into tb_request(type_id, progress, date_completion, data, user_id) values 
                          (%(type_id)s, %(progress)s, %(date_completion)s, %(data)s, %(user_id)s)""",
                          {"type_id": type_id, "progress": progress,
                           "data": data, "user_id": user_id,
                           "date_completion": None})
        self.__db_connection.commit()

    def store_video(self, video: dict, video_id: str) -> bool:
        self.__db.execute("""insert into tb_video(description, duration, like_count, published_at, view_count, comment_count, language, channel_id, yt_id) values 
                          (%(description)s, %(duration)s, %(like_count)s, %(published_at)s, 
                          %(view_count)s, %(comment_count)s, %(language)s, %(channel_id)s, %(yt_id)s) ON CONFLICT (yt_id) DO NOTHING""",
                          {"description": video["description"], "duration": video["duration"],
                           "like_count": video["likeCount"] if video["likeCount"] else 0,
                           "published_at": video["publishedAt"],
                           "view_count": video["viewCount"] if video["viewCount"] else 0,
                           "comment_count": video["commentCount"] if video["commentCount"] else 0,
                           "language": video["defaultLanguage"] if video["defaultLanguage"] else 0,
                           "channel_id": video["channelId"], "yt_id": video_id, })
        self.__db_connection.commit()

        return True

    def store_comments(self, comments: dict) -> None:
        for comment in comments:
            if not comment["isReply"]:
                self.__db.execute("""insert into tb_comment(original_text, author_display_name, like_count, published_at, updated_at, total_reply_count, video_id, yt_id) values 
                                (%(original_text)s, %(author_display_name)s, %(like_count)s, %(published_at)s, 
                                %(updated_at)s, %(total_reply_count)s, %(video_id)s, %(yt_id)s) ON CONFLICT (yt_id) DO NOTHING""",
                                  {"original_text": comment["textOriginal"],
                                   "author_display_name": comment["authorDisplayName"],
                                   "like_count": comment["likeCount"], "published_at": comment["publishedAt"],
                                   "updated_at": comment["updatedAt"], "total_reply_count": comment["totalReplyCount"],
                                   "video_id": comment["videoId"], "yt_id": comment["id"], })
                self.__db_connection.commit()
            else:
                self.__db.execute("""insert into tb_comment(original_text, author_display_name, like_count, published_at, updated_at, total_reply_count, video_id, yt_id) values 
                                (%(original_text)s, %(author_display_name)s, %(like_count)s, %(published_at)s, 
                                %(updated_at)s, %(total_reply_count)s, %(video_id)s, %(yt_id)s) ON CONFLICT (yt_id) DO NOTHING""",
                                  {"original_text": comment["textOriginal"],
                                   "author_display_name": comment["authorDisplayName"],
                                   "like_count": comment["likeCount"], "published_at": comment["publishedAt"],
                                   "updated_at": comment["updatedAt"], "total_reply_count": 0,
                                   "video_id": comment["videoId"], "yt_id": comment["id"], })
                self.__db_connection.commit()

                # self.__db.execute("""insert into tb_comment_replies (from_comment_id, to_comment_id)
                #                         select
                #                             c.id,
                #                             r.id,
                #                         from tb_comment c
                #                         inner join tb_comment r
                #                         on r.RoleId = u.RoleId
                #                         and c.yt_id = %(parentId)s""", {"parentId": comments["parentId"]})
                # self.__db_connection.commit()

    def get_comments(self, video_id) -> list:
        query = "SELECT * FROM tb_comment WHERE video_id = %s"
        self.__db.execute(query, (video_id,))
        return self.__db.fetchall()

    def get_videos(self, channel_id) -> dict:
        query = "SELECT * FROM tb_video WHERE channel_id = %s"
        self.__db.execute(query, (channel_id,))
        videos = {}
        for video in self.__db.fetchall():
            videos[video['video_id']] = video
        return videos

    def get_video(self, video_id: str) -> dict:
        query = "SELECT * FROM tb_video WHERE yt_id = %s"
        self.__db.execute(query, (video_id,))
        return self.__db.fetchone()

    def pre_update_request(self, request: list):
        filter_query = "SELECT * FROM tb_request WHERE id = %s"
        self.__db.execute(filter_query, (request[0],))
        exists = self.__db.fetchone()

        if exists:
            update_query = "UPDATE tb_request SET progress = 0 WHERE id = %s"
            self.__db.execute(update_query, (request[0],))
        else:
            update_query = "INSERT INTO tb_request VALUES (%s, %s, %s, %s,%s)"
            self.__db.execute(update_query, (request[0], request[1], 0, None, request[3],))
        self.__db_connection.commit()
        return exists is not None

    def get_scraper_request(self, low_bound, upper_bound):
        query = """
            SELECT * FROM tb_request 
            WHERE type_id >= %s AND type_id <= %s AND progress = 1
            LIMIT 1
        """
        self.__db.execute(query, (low_bound, upper_bound))
        return self.__db.fetchone()

    def store_analisis(self, element_id, metric, param, user_id):
        data = {
            'id': element_id,
            'metric': metric,
            'type': param,
            'updated': datetime.today().isoformat()
        }
        print("***",data)
        filter_query = "SELECT * FROM tb_calculation_result WHERE yt_id = %s AND type_id = %s AND user_id = %s"
        self.__db.execute(filter_query, (element_id, param, user_id))
        exists = self.__db.fetchone()
        metric = json.dumps(metric, default=str)
        if exists:
            update_query = """
                UPDATE tb_calculation_result 
                SET result = %s
                WHERE yt_id = %s AND type_id = %s AND user_id = %s
            """
            self.__db.execute(update_query, (metric, element_id, param, user_id ))
        else:
            update_query = """
                INSERT INTO tb_calculation_result (result, user_id, yt_id, type_id) 
                VALUES (%s, %s, %s, %s)
            """
            self.__db.execute(update_query, (metric, user_id, element_id, param))
        self.__db_connection.commit()
        return exists is not None

    def is_channel_exists(self, channel_id: str):
        query = "SELECT 1 FROM tb_channel WHERE channel_id = %s"
        self.__db.execute(query, (channel_id,))
        return self.__db.fetchone() is not None

    def is_video_exists(self, video_id: str):
        query = "SELECT * FROM tb_video WHERE yt_id = %s"
        self.__db.execute(query, (video_id,))
        return self.__db.fetchone() is not None

    def get_all_metrics(self, metric_type):
        query = "SELECT * FROM tb_calculation_result WHERE type_id = %s"
        self.__db.execute(query, (metric_type,))
        return self.__db.fetchall()

    def get_metric(self, video_id, metric_type):
        if self.is_video_exists(video_id):
            query = "SELECT * FROM tb_calculation_result WHERE type = %s AND id = %s"
            self.__db.execute(query, (metric_type, video_id))
            return self.__db.fetchone()
        return {}
    
    def update_comment_emotions(self, emotions: dict, batch_size: int = 1000) -> bool:
        """
        Update the emotion field in the tb_comment table using batching for large datasets.

        Args:
            emotions (dict): A dictionary mapping comment IDs to emotion IDs.
            batch_size (int): The number of updates to process in a single batch. Default is 1000.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        try:
            # Convert dictionary to a list of tuples for processing
            data = [(emotion_id + 1, comment_id) for comment_id, emotion_id in emotions.items()]
            
            # Split the data into batches
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                
                # Generate SQL for bulk update in batch
                placeholders = ', '.join(['(%s, %s)'] * len(batch))
                update_emotion_query = f"""
                    UPDATE tb_comment 
                    SET emotion_id = data_table.emotion
                    FROM (VALUES {placeholders}) AS data_table(emotion, yt_id)
                    WHERE tb_comment.yt_id = data_table.yt_id
                """
                
                # Flatten batch data for parameterized query
                flattened_data = [item for pair in batch for item in pair]
                
                # Execute the batch update
                self.__db.execute(update_emotion_query, flattened_data)
                self.__db_connection.commit()
            
            logging.info("Emotions updated successfully in tb_comment table using batch updates.")
            return True
        except Exception as e:
            logging.error(f"Failed to update emotions in tb_comment table using batch updates: {e}")
            self.__db_connection.rollback()
            return False


        
    
