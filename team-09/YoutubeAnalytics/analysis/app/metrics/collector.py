from collections import Counter
from datetime import datetime

from app.metrics.loader import Loader

from app.config.requests_types import *
from app.metrics.plots import *


class Collector:
    def __init__(self, db=None):
        self.loader = Loader(db=db)

    def collect_metric(self, metric_type: int, channel_id):
        data = {}
        videos = self.loader.db.get_videos(channel_id)
        for video in videos:
            print(video)
            self.loader.load_metric(metric_type, channel_id, video)
            new_data = self.loader.metrics[channel_id][metric_type]
            for i in new_data.keys():
                if i in data.keys():
                    if isinstance(data[i], dict):
                        data[i].update(new_data[i])
                    else:
                        data[i] += new_data[i]
                else:
                    data[i] = new_data[i]
        if metric_type == GET_ANALYSIS_OF_TIME:
            pub_times = []
            for video in videos:
                pub_times.append(datetime.fromisoformat(videos[video]['publishedAt'].replace('Z', '+00:00')))
            datetime_counts = Counter()
            for entry in data['0']:
                datetime_entry = entry  # Convert to datetime object
                datetime_counts[datetime_entry] += 1

            # Sort the entries by datetime
            sorted_counts = sorted(datetime_counts.items(), key=lambda x: x[0])
            # Extract datetime and cumulative counts
            datetimes = [date for date, _ in sorted_counts]
            counts = [count for _, count in sorted_counts]
            cumulative_counts = [sum(counts[:i + 1]) for i in range(len(counts))]
            graph_counts_by_datetime(datetimes,cumulative_counts, channel_id, pub_times)
        elif metric_type == GET_ANALYSIS_OF_LANGUAGES:
            sizes = [i for i in data.values()]
            labels = [i for i in data.keys()]
            graph_count_langs(sizes, labels, channel_id)
        elif metric_type == GET_ANALYSIS_OF_EMOTION:
            sizes = [i for i in data.values()]
            labels = [i for i in data.keys()]
            graph_counts_emotion(labels, sizes, channel_id)
        elif metric_type == GET_ANALYSIS_OF_LIKES_VS_REPLIES:
            reply_counts = data['reply_count']
            like_counts = data['like_count']
            graph_like_vs_replies_counts(reply_counts, like_counts, channel_id)
        elif metric_type == GET_ANALYSIS_OF_NEQ_POS:
            pos = data['Positive Comments']
            neg = data['Negative Comments']
            neu = data['Neutral Comments']
            graph_counts_neg_and_pos([pos, neg, neu],\
                ['Positive Comments','Negative Comments','Neutral Comments'],channel_id)
        elif metric_type == GET_POPULARITY:
            pass
        elif metric_type == GET_WORD_MAP:
            pass

