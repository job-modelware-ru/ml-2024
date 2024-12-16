import logging

from matplotlib import pyplot as plt
from wordcloud import WordCloud


def graph_counts_by_datetime(datetimes, cumulative_counts, name, pub_time=None):
    if pub_time is None:
        pub_time = []
    plt.figure(figsize=(12, 6))
    plt.plot(datetimes, cumulative_counts, marker='o', linestyle='-', color='blue')
    for i in pub_time:
        plt.axvline(x=i, linestyle='--', color='red')
    plt.xlabel('Date and Time')
    plt.ylabel('Count of comments')
    plt.title(f'Count of comments {name}')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    logging.basicConfig(level=logging.INFO,
                        filename="analysis/analysis.log", format="%(asctime)s %(levelname)s %(message)s")
    plt.savefig(f'Comments_count_of_{name}.png')


def graph_counts_neg_and_pos(sizes: list, labels: list, name):
    colors = ['#66ff66', '#ff6666', '#999999']  # Green for positive, red for negative, gray for neutral
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.axis('equal')
    plt.savefig(f'Comments_neg_and_pos_count_of_{name}.png')


def graph_counts_emotion(labels, sizes, name):
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.axis('equal')
    plt.savefig(f'Comments_emotion_count_of_{name}.png')


def graph_like_vs_replies_counts(reply_counts, like_counts, name):
    plt.scatter(reply_counts, like_counts, color='blue', alpha=0.5)
    plt.title(f'Like Count vs Reply Count {name}')
    plt.xlabel('Reply Count')
    plt.ylabel('Like Count')
    plt.savefig(f'Comments_likes_by_replies{name}.png')


def graph_count_langs(sizes, labels, name):
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.axis('equal')
    plt.savefig(f'Comments_neg_and_pos_count_of_{name}.png')


def graph_word_map(freq, pos_freq, neg_freq, video_name):
    wordcloud = WordCloud(width=2000,
                          height=1500,
                          random_state=1,
                          background_color='black',
                          relative_scaling=1,
                          margin=20,
                          colormap='Pastel1',
                          collocations=False).generate_from_frequencies(freq)
    wordcloud.to_file(f'Word_cloud_all_{video_name}.png')
    wordcloud_pos = WordCloud(width=2000,
                              height=1500,
                              random_state=1,
                              background_color='black',
                              relative_scaling=1,
                              margin=20,
                              colormap='Pastel1',
                              collocations=False).generate_from_frequencies(pos_freq)
    wordcloud_pos.to_file(f'Word_cloud_pos_{video_name}.png')
    wordcloud_neg = WordCloud(width=2000,
                              height=1500,
                              random_state=1,
                              background_color='black',
                              relative_scaling=1,
                              margin=20,
                              colormap='Pastel1',
                              collocations=False).generate_from_frequencies(neg_freq)
    wordcloud_neg.to_file(f'Word_cloud_neg_{video_name}.png')
