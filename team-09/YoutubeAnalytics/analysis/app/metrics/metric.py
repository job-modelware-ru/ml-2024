from collections import defaultdict

import numpy as np
from emotion_analisis.analyser import Analyser
from metrics.plots import *
from stop_words import safe_get_stop_words

"""
Calculates metric -- number of comments depending on publication time
"""

from collections import Counter
from datetime import datetime, timezone


def plot_counts_by_datetime(comments: dict, video_name: str, make_plot: bool = False, return_count=False) -> list:
    # Extract the time information and count occurrences cumulatively
    datetime_counts = Counter()
    for entry in comments.values():
        #datetime_entry = datetime.fromisoformat(entry[5][:-1])  # Convert to datetime object
        datetime_counts[entry[5]] += 1

    # Sort the entries by datetime
    sorted_counts = sorted(datetime_counts.items(), key=lambda x: x[0])
    # Extract datetime and cumulative counts
    datetimes = [date for date, _ in sorted_counts]
    counts = [count for _, count in sorted_counts]

    # Perform cumulative sum for the counts
    cumulative_counts = [sum(counts[:i + 1]) for i in range(len(counts))]
    if make_plot:
        graph_counts_by_datetime(datetimes, cumulative_counts, video_name)
    if return_count:
        return [datetimes, counts]
    return [datetimes, cumulative_counts]


def plot_counts_neg_and_pos(comments: dict, video_name: str, make_plot: bool = False, analyser: Analyser = None):
    if analyser is None:
        analyser = Analyser()
    if analyser.result is None or len(analyser.result.values()) > 0\
            and next(iter(analyser.result.values())).get('sentiment') is None:
        d_type = {'sentiment': True}
        analyser.analyse_comments(comments, d_type)
    positive_comments_count = 0
    negative_comments_count = 0
    neutral_comments_count = 0
    for entry in analyser.result.values():
        if entry['sentiment'].output == 'NEG':
            negative_comments_count += 1
        if entry['sentiment'].output == 'POS':
            positive_comments_count += 1
        if entry['sentiment'].output == 'NEU':
            neutral_comments_count += 1
    labels = ['Positive Comments', 'Negative Comments', 'Neutral Comments']
    sizes = [positive_comments_count, negative_comments_count, neutral_comments_count]
    if make_plot:
        graph_counts_neg_and_pos(sizes, labels, video_name)

    return dict(zip(labels, sizes))


def plot_counts_emotion(comments: dict, video_name: str, make_plot: bool = False, analyser: Analyser = None):
    print("plot")
    if analyser is None:
        analyser = Analyser()
    if analyser.result is None or len(analyser.result.values()) > 0 and \
            next(iter(analyser.result.values())).get('emotion') is None:
        d_type = {'emotion': True}
        res = analyser.analyse_comments(comments, d_type)
        print("stop", res)
    label_to_emotion = {
        0: "sadness",
        1: "joy",
        2: "love",
        3: "anger",
        4: "fear",
        5: "surprise",
        6: "neutral"
    }
    print(label_to_emotion)
    types = label_to_emotion.values()
    print(types)
    counts = dict(zip(types, [0] * len(types)))
    for entry in analyser.result.values():
        for t in label_to_emotion.values():
            if entry['emotion'].output == t:
                counts[t] += 1
    print(counts)

    sizes = [i for i in counts.values()]
    if make_plot:
        graph_counts_emotion(types, sizes, video_name)
    return counts


def plot_like_vs_replies_counts(comments: dict, video_name: str, make_plot: bool = False):
    reply_count_dict = defaultdict(int)
    like_count_dict = defaultdict(int)
    for comment_id, comment_info in comments.items():
        is_reply = comment_info.get('isReply', False)
        # like_count = comment_info.get('likeCount', 0)
        parent_id = comment_info.get('parentId', None)
        reply_count = comment_info.get('totalReplyCount',0)
        reply_count_dict[comment_id] += reply_count
    for comment_id in reply_count_dict.keys():
        like_count_dict[comment_id] = comments[comment_id].get('likeCount', 0)
    reply_counts = list(reply_count_dict.values())
    like_counts = list(like_count_dict.values())
    if make_plot:
        graph_like_vs_replies_counts(reply_counts, like_counts, video_name)
    return {'reply_count': reply_count_dict, 'like_count': like_count_dict}


def plot_counts_langs(comments: dict, video_name: str, make_plot: bool = False, analyser: Analyser = None):
    if analyser is None:
        analyser = Analyser()
    if analyser.result is None or len(analyser.result.values()) > 0 and \
            next(iter(analyser.result.values())).get('lang') is None:
        d_type = {'lang': True}
        analyser.analyse_comments(comments, d_type)
    counts = dict()
    for entry in analyser.result.values():
        if entry['lang'][0]['label'] not in counts.keys():
            counts[entry['lang'][0]['label']] = 0
        counts[entry['lang'][0]['label']] += 1
    sizes = [i for i in counts.values()]
    labels = list(counts.keys())
    if make_plot:
        graph_count_langs(sizes, labels, video_name)
    return counts


def plot_word_map(comments: dict, video_name: str, make_plot: bool = False, analyser: Analyser = None):
    if analyser is None:
        analyser = Analyser()  # todo think about what if only two comments
    if analyser.result is None or \
            (len(analyser.result.values()) > 0 and \
             next(iter(analyser.result.values())).get('lang') is None
             and analyser.result.get('sentiment') is None):
        d_type = {'lang': True,
                  'sentiment': True}
        analyser.analyse_comments(comments, d_type)
    # text = analyser.result.pop('word_count')
    text = analyser.result
    counts = set()
    pos_freq = defaultdict(int)
    neg_freq = defaultdict(int)
    freq = defaultdict(int)
    for key in analyser.result.keys():
        entry = analyser.result[key]
        sentence = comments[key][1] if comments[key][1] is not None else ''
        words = "".join(c for c in sentence if c.isalnum() or c.isspace())
        words = words.lower().split()
        for word in words:
            freq[word] += 1
            if entry['sentiment'].output == 'POS':
                pos_freq[word] += 1
            if entry['sentiment'].output == 'NEG':
                neg_freq[word] += 1
        if entry['lang'][0]['label'] not in counts:
            counts.add(entry['lang'][0]['label'])

    stop_words = []
    for lang in list(counts):
        stop_words += safe_get_stop_words(lang)
    stop_words = set(stop_words)

    for item in stop_words:
        if item in freq:
            del freq[item]
            if item in pos_freq.keys():
                del pos_freq[item]
            if item in neg_freq.keys():
                del neg_freq[item]
    if make_plot:
        graph_word_map(freq, pos_freq, neg_freq, video_name)

    return {'all_freq': freq, 'pos_freq': pos_freq, 'neg_freq': neg_freq}


def create_popularity_metrics(comments: dict,video_info:dict, video_name: str, analyser: Analyser = None, print_metrics=False):
    datetimes, cumulative_counts = plot_counts_by_datetime(comments, video_name)
    analyser = Analyser()
    metric_emotion = plot_counts_emotion(comments, video_name, analyser=analyser)
    # metric_likes_vs_replies = plot_like_vs_replies_counts(comments, video_name)
    metric_neq_pos = plot_counts_neg_and_pos(comments, video_name, analyser=analyser)
    favorite_count = int(video_info.get('favoriteCount', 0))
    comments_count = int(video_info.get('commentCount'), 0)
    likes_count = int(video_info.get('likeCount', 0))
    puplished_at = datetime.fromisoformat(video_info.get('publishedAt').replace('Z', '+00:00'))
    view_count = int(video_info.get('viewCount', 0))
    comments_size = len(cumulative_counts)
    comments_time_comp = 1
    if comments_size > 0:
        deltas = [(datetimes[i + 1] - datetimes[i]).seconds / 3600.0 for i in range(len(datetimes) - 1)]
        # calculate the first derivative of the count over time
        derivatives = [1.0 / deltas[i] for i in
                       range(len(cumulative_counts) - 1)]
        counts_coeff = int(np.log2(comments_size) if comments_size != 1 else 1)
        comments_time_comp = np.mean(derivatives[:-counts_coeff])
        if comments_time_comp < 1:
            comments_time_comp = 1
    spam = 1+np.abs(comments_count - comments_size)/(max(comments_count, comments_size))
    time_delta = (datetime.now(timezone.utc) - puplished_at).total_seconds() / 60.0
    time_coeff = (likes_count + view_count*0.01)/time_delta
    comment_coeff = spam * comments_time_comp
    em_coeff = (metric_neq_pos['Positive Comments'] + metric_neq_pos['Negative Comments'])/comments_size
    popularity = time_coeff + \
                 + favorite_count*25 + comment_coeff * em_coeff
    emotional_response = (metric_emotion['surprise'] + metric_emotion['joy']) - \
                         (metric_emotion['sadness'] + metric_emotion['anger'] + \
                          metric_emotion['fear']+metric_emotion['disgust'])
    if print_metrics:
        print('comments:', comments_size)
        print("spam:", spam)
        print("time_delta", time_delta)
        print("emotions",metric_emotion)
        print("p_n:", metric_neq_pos)
        print("likes", likes_count)
        print("views", view_count)
        print("time_coeff", time_coeff)
        print("deriv",comments_time_comp, derivatives[-counts_coeff])
        print("commets_coef", comment_coeff)
        print("em_coeff", em_coeff)
        print("poularity", popularity)
        print("response", emotional_response)


    return {'popularity':popularity, 'emotional_response':emotional_response}
