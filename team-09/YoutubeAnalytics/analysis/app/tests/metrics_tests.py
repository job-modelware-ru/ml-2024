import json
import unittest

from matplotlib import pyplot as plt
from matplotlib.dates import num2date

from app.db.db import DataBase
from app.emotion_analisis.analyser import Analyser
from app.metrics.loader import Loader

from app.metrics.metric import *

from app.metrics.collector import Collector


class TestAnalisis(unittest.TestCase):
    def test_sentiment(self):
        test_comment_text = 'Love this video'
        analyser = Analyser()
        res = analyser.analyse_sentiment(test_comment_text)

    def test_plot_time(self):
        test_video_id = 'q_ve9SsuyvU'
        test_channel_id = 'UCzdmz_lLWT_dPqOvFjXAMVg'
        loader = Loader([test_channel_id])
        comments = loader.get_all_comments(test_channel_id, test_video_id)
        plot_counts_by_datetime(comments, test_video_id)

    def test_plot_pos_neg_count(self):
        test_video_id = 'g_sA8hYU3b8'
        test_channel_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([test_channel_id])
        comments = loader.get_all_comments(test_channel_id, test_video_id)
        plot_counts_neg_and_pos(comments, test_video_id, make_plot=True)

    def test_plot_emotion(self):
        test_video_id = 'g_sA8hYU3b8'
        test_channel_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([test_channel_id])
        comments = loader.get_all_comments(test_channel_id, test_video_id)
        plot_counts_emotion(comments, test_video_id, make_plot=True)

    def test_pie_plot(self):
        sizes = [20, 10, 70]
        labels = ['Positive Comments', 'Negative Comments', 'Neutral Comments']
        colors = ['#66ff66', '#ff6666', '#999999']  # Green for positive, red for negative, gray for neutral
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.axis('equal')
        plt.savefig(f'Comments_neg_and_pos_count_of_test.png')

    def test_emotions_calc(self):
        types = ['others', 'joy', 'sadness', 'anger', 'surprise', 'disgust', 'fear']
        plt.pie([i for i in range(len(types))], labels=types, autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        plt.axis('equal')
        plt.savefig(f'Comments_emotion_test.png')

    def test_plot_like_vs_replies_counts(self):
        test_video_id = 'q_ve9SsuyvU'
        test_channel_id = 'UCzdmz_lLWT_dPqOvFjXAMVg'
        loader = Loader([test_channel_id])
        comments = loader.get_all_comments(test_channel_id, test_video_id)
        plot_like_vs_replies_counts(comments, test_video_id, make_plot=True)

    def test_plot_langs(self):
        test_video_id = 'q_ve9SsuyvU'
        test_channel_id = 'UCzdmz_lLWT_dPqOvFjXAMVg'
        loader = Loader([test_channel_id])
        comments = loader.get_all_comments(test_channel_id, test_video_id)
        plot_counts_langs(comments, test_video_id, make_plot=True)

    def test_plot_ru_langs(self):
        comments = {
            'test1':{
            'id':'test',
            'textOriginal':"Мне нравится"}
        }
        plot_counts_langs(comments, 'test_name', make_plot=True)
    def test_all(self):
        v_id ='g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        mets = create_all_metrics(comments, v_id, True)

    def test_word_cloud(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        wc = plot_word_map(comments, v_id, True)
    def test2_word_cloud(self):
        v_id = 'CWpNfecqW54'
        ch_id = 'UCg40OxZ1GYh3u3jBntB6DLg'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        wc = plot_word_map(comments, v_id, True)
    def test_popularity(self):
        v_id = 'g_sA8hYU3b8'
        ch_id = 'UConVfxXodg78Tzh5nNu85Ew'
        loader = Loader([ch_id])
        comments = loader.get_all_comments(ch_id, v_id)
        video = loader.load_video(v_id)
        mts = create_popularity_metrics(comments, video, v_id,print_metrics=True)
    def test_collect(self):
        # our channel
        ch_id = 'UC4PoyiMa9Ha0SDRyRNDA_Qw'
        db = DataBase()
        db.create_connection()
        collector = Collector(db)
        collector.collect_metric(7, ch_id)
        db.close_connection()

    def test_collect_31_video(self):
        # our channel
        ch_id = 'UCLB7AzTwc6VFZrBsO2ucBMg'
        db = DataBase()
        db.create_connection()
        collector = Collector(db)
        collector.collect_metric(7, ch_id)
        db.close_connection()

    def test_collect_big_video(self):
        # our channel
        ch_id = 'UCLXo7UDZvByw2ixzpQCufnA'
        db = DataBase()
        db.create_connection()
        collector = Collector(db)
        collector.collect_metric(7, ch_id)
        db.close_connection()
    def test_graph_3d(self):
        with open(f'C:\\Users\\Aleksandr\\Downloads\\Telegram Desktop\\output1.txt', 'r') as file:
            data = json.load(file)
            x = np.array(data["date"])
            # arr1inds = x.argsort()
            x = np.sort(x)
            x_t = num2date(x)
            y = np.array(data["count"])
            # Вычисляем плотность распределения точек с помощью функции `gaussian_kde`
            from scipy.stats import gaussian_kde
            xy = np.vstack([x, y])
            density = gaussian_kde(xy)(xy)

            # Создаем новую фигуру и оси для графика
            fig, ax = plt.subplots()

            # Используем scatter plot для отображения точек с учетом плотности распределения
            ax.scatter(x_t, y, c=density, cmap='viridis', edgecolors='black')

            # Добавляем цветовую шкалу
            cbar = plt.colorbar(mappable=None, cax=None, ax=None)
            cbar.set_label('Density')

            # Добавляем подписи для осей
            ax.set_xlabel('X')
            ax.set_ylabel('Y')

            # Отображаем график
            plt.savefig('big.png')

if __name__ == '__main__':
    unittest.main()