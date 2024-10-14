import face_recognition
import numpy as np
import cv2


# векторные представления лиц, имена, user_id в БД
known_face_encodings, known_face_names, known_face_uids = [], [], []

def run_rec():
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while video_capture.isOpened():
        # чтение кадра с камеры
        ret, frame = video_capture.read()
        # уменьшение разрешения (для быстродействия)
        divideint = 2
        small_frame = cv2.resize(frame, (0, 0), 
   fx=1 / divideint, fy=1 / divideint)
        # уменьшение размерности матрицы изображения, аналог [:, :, ::-1] 
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        # обрабатывается каждый 3й кадр (для быстродействия)
        if process_this_frame % 3 == 0:
            # расположение лиц
            face_locations = face_recognition.face_locations(rgb_small_frame)
            # преобразование лиц в векторы
            face_encodings = face_recognition.face_encodings(rgb_small_frame, 
  face_locations)
            # сравнение обнаруженных лиц с лицами в базе
            for face_encoding in face_encodings:
                name = "Unknown"
                # вычисление векторного расстояния (мера схожести векторов)
                # known_face_encodings - 
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                # определение индекса максимально похожего лица
                best_match_index = np.argmin(face_distances)
                # проверка на степень похожести 
                # похожи если векторное расстояние расстояние меньше 0.6
                if face_distances[best_match_index] < 0.6:
                    # имя обнаруженного лица для пользователя
                    name = known_face_names[best_match_index]
                    # user_id лица для внутреннего использования
                    uid = known_face_uids[best_match_index]
