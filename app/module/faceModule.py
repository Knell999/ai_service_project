import cv2
import numpy as np
from tensorflow.keras.models import load_model



class face_anlysis:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = cv2.imread(file_path)
        self.resize_image = None
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            print(len(faces))
            (x, y, w, h) = faces[0]
            cropped = self.image[y : y + h, x : x + w]  # 얼굴 영역만큼 crop
            self.resize_image = cv2.resize(cropped, (150, 150))  # 이미지 사이즈 재조정
        else:
            print("얼굴이 없습니다.")

    def similar_face(self):
        # 모델이 기대하는 형태로 차원 추가 (batch 차원 추가)
        input_image = np.expand_dims(self.resize_image, axis=0)

        # 이미지를 0과 1사이의 값으로 조정 (정규화)
        input_image = input_image / 255.0

        celebrityModel = load_model("model/inceptionV3_celebrity.h5")

        # 입력 이미지에 대한 연예인 얼굴 예측
        pred = celebrityModel.predict(input_image)

        # 학습시켰던 연예인 이름 레이블
        class_labels = ["이승기", "남주혁", "박보영", "서강준"]

        # 가장 큰 원소의 인덱스를 반환
        predict_class_index = np.argmax(pred)

        # 가장 높은 확률을 가진 클래스의 레이블명 반환
        predict_label = class_labels[predict_class_index]

        probability = round(pred[0][predict_class_index] * 100, 2)

        result = {'Celeb':f'{predict_label}', 'Probability':f'{probability}'}

        return result
    
    def gender_detector(self):
        gender_list = ['남성', '여성'] # 성별 클래스

        # 성별 및 연령 예측을 위한 이미지 변환 맟 전처리
        blob = cv2.dnn.blobFromImage(self.resize_image, 1, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)

        # 성별 예측 모델 불러오기
        gender_net = cv2.dnn.readNetFromCaffe(
            'model/gender_deploy.prototxt',
            'model/gender_net.caffemodel')

        # 성별 탐지
        gender_net.setInput(blob)
        gender_preds = gender_net.forward()

        gender_class = gender_preds.argmax() # 가장 높은 Score값을 선정
        gender = gender_list[gender_class]
        gender_probability = round(gender_preds[0][gender_class]*100, 2)

        result = {'Gender':f'{gender}', 'Probability':f'{gender_probability}'}
        return result
    
    def age_detector(self):
        age_list = ['0~2','4~6','8~12','15~20','25~32','38~43','48~53','60~100'] # 나이대 리스트
        
        # 성별 및 연령 예측을 위한 이미지 변환 맟 전처리
        blob = cv2.dnn.blobFromImage(self.resize_image, 1, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)

        # 성별 예측 모델 불러오기
        age_net = cv2.dnn.readNetFromCaffe(
            'model/age_deploy.prototxt',
            'model/age_net.caffemodel')

        # 성별 탐지
        age_net.setInput(blob)
        age_preds = age_net.forward()

        age_class = age_preds.argmax() # 가장 높은 Score값을 선정
        age = age_list[age_class]
        age_probability = round(age_preds[0][age_class]*100, 2)

        result = {'age':f'{age}', 'Probability':f'{age_probability}'}
        return result
    
    def animal_detector(self):
        animal_list = ['치타', '고양이', '강아지', '여우', '사막여우', '늑대']

        # 모델이 기대하는 형태로 차원 추가 (batch 차원 추가)
        input_image = np.expand_dims(self.resize_image, axis=0)

        # 이미지를 0과 1사이의 값으로 조정 (정규화)
        input_image = input_image/255.0

        # 모델 불러오기
        celebrityModel = load_model("model/inceptionV3_animal.keras")

        # 입력 이미지에 대한 예측
        pred = celebrityModel.predict(input_image)
        pred_index = np.argmax(pred)

        animal = animal_list[pred_index]
        probability = round(pred[0][pred_index]*100, 2)

        result = {'animal':animal, 'Probability':probability}
        return result
    
    def race_detector(self):
        race_list = ['아시아인', '백인', '인도인', '흑인']

        # 모델이 기대하는 형태로 차원 추가 (batch 차원 추가)
        input_image = np.expand_dims(self.resize_image, axis=0)

        # 이미지를 0과 1사이의 값으로 조정 (정규화)
        input_image = input_image/255.0

        # 모델 불러오기
        raceModel = load_model("model/race_model.h5")

        # 입력 이미지에 대한 예측
        pred = raceModel.predict(input_image)
        pred_index = np.argmax(pred)

        race = race_list[pred_index]
        probability = round(pred[0][pred_index]*100, 2)

        result = {'race':race, 'Probability':probability}
        return result
