import cv2
import numpy as np
from tensorflow.keras.models import load_model

class face_anlysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = cv2.imread(file_path)
        self.resize_image = None

        face_cascade = cv2.CascadeClassifier('model/haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(self.image , cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3 ,5)
        if len(faces) > 0:
            print(len(faces))
            (x, y, w, h) = faces[0]
            cropped = self.image[y: y+h, x:x+w] # 얼굴 영역만큼 crop
            self.resize_image = cv2.resize(cropped, (150, 150)) # 이미지 사이즈 재조정

        else:
            print('얼굴이 없습니다.')

    def similar_face(self):
        # 모델이 기대하는 형태로 차원 추가 (batch 차원 추가)
        input_image = np.expand_dims(self.resize_image, axis=0)

        # 이미지를 0과 1사이의 값으로 조정 (정규화)
        input_image = input_image/255.0

        celebrityModel = load_model('model/inceptionV3_celebrity.h5')

        # 입력 이미지에 대한 연예인 얼굴 예측
        pred = celebrityModel.predict(input_image)

        # 학습시켰던 연예인 이름 레이블
        class_labels = ['이승기', '남주혁', '박보영', '서강준']

        # 가장 큰 원소의 인덱스를 반환
        predict_class_index = np.argmax(pred)

        # 가장 높은 확률을 가진 클래스의 레이블명 반환
        predict_label = class_labels[predict_class_index]

        c_result = f'당신이 {predict_label}일 확률은 {round(pred[0][predict_class_index]*100, 2)}% 입니다!'
        return c_result
    
    # def gender_detector(self):
    #     gender_list = ['남성', '여성'] # 성별 클래스
    #     MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

    #     # 성별 및 연령 예측을 위한 이미지 변환 맟 전처리
    #     blob = cv2.dnn.blobFromImage(image, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

    #     # 성별 예측 모델 불러오기
    #     gender_net = cv2.dnn.readNetFromCaffe(
    #         'models/gender_deploy.prototxt',
    #         'models/gender_net.caffemodel')

    #     # 성별 탐지
    #     gender_net.setInput(blob)
    #     gender_preds = gender_net.forward()

    #     gender_class = gender_preds.argmax() # 가장 높은 Score값을 선정
    #     gender = gender_list[gender_class]
    #     gender_probability = round(gender_preds[0][gender_class]*100, 2)

    #     return