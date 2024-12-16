from sshtunnel import SSHTunnelForwarder
import logging
from googleapiclient.errors import HttpError
from data.app.db.db import DataBase
from data.app.db.config import *
from data.app.core.youtube import Youtube
from data.app.core.requests_func import requests_func, requests_quota_size
import json
import time


MAX_TASKS_NUM = 100

port = 5432
ssh_connection = False
if ssh_connection:
   server = SSHTunnelForwarder(ssh_ip, ssh_username=ssh_username,
                                       ssh_password=ssh_password, remote_bind_address=(db_ip, db_port))

   server.start()

   port = server.local_bind_port

def main(db: DataBase) -> None:
   youtube_api = None
   youtube = None
   last_request_fetching = 0
   requests = []

   while True:
      try:
         db.reset_api_quota()
         if len(requests) == 0:
            requests = db.get_scraper_requests(0, 6, MAX_TASKS_NUM)

         if len(requests) == 0:
            time.sleep(10)
            continue

         request = requests.pop(0)

         request_id = request[0]
         request_type = request[1]
         request_data = json.loads(request[2])
         request_progress = request[3]
         request_user_id = request[4]

         request_quota_size = requests_quota_size[request_type]

         new_youtube_api = db.get_available_api(request_quota_size)

         if not new_youtube_api:
            time.sleep(10)
            continue

         if youtube_api is None or youtube_api["key"] != new_youtube_api["key"]:
            youtube_api = new_youtube_api

            youtube = Youtube(youtube_api["key"])

         requests_func[request_type](youtube, request_data, db, request_user_id)
         youtube_api["quota"] = youtube_api["quota"] - request_quota_size
         db.update_api_quota(youtube_api["key"], youtube_api["quota"])

         print(json.dumps(request_data))
         request_progress -= 1
         db.update_scraper_request(request_id, request_progress, json.dumps(request_data))

      except HttpError as e:
         print(e)

if __name__ == "__main__":
   print("To exit the application, press Ctrl-c")

   logging.basicConfig(level=logging.INFO,
                  filename="data.log", format="%(asctime)s %(levelname)s %(message)s")

   db = DataBase()
   db.create_connection(port)

   try:
      main(db)
   except KeyboardInterrupt:
      logging.info("Ctrl-c was pressed")

   db.close_connection()

   if server:
      server.stop()