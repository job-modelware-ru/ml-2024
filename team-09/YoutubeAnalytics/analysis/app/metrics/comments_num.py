from app.db.db import DataBase
from numpy import ndarray


def comments_size(db: DataBase, video_id: str) -> list:
    comments = db.get_comments(video_id, {"id": 1, "textDisplay": 1})

    comments_size = ndarray((len(comments))).astype("int")
    for i, comment in enumerate(comments):
        comments_size[i] = len(comment["textDisplay"])

    return comments_size
