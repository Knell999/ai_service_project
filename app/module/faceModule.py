import io
import base64

import cv2
import torch
from torchvision import transforms
from PIL import Image
from facenet_pytorch import MTCNN

mtcnn = MTCNN()


class FaceAnalysis:
    def __init__(self, file_path, model_path, class_labels):
        self.file_path = file_path
        self.model_path = model_path
        self.class_labels = class_labels
        self.model = self.load_model()

    def load_model(self):
        return torch.load(self.model_path)

    def read_image(self):
        color = cv2.imread(self.file_path)
        return cv2.cvtColor(color, cv2.COLOR_RGBA2RGB)

    def face_extraction(self, image):
        # Detect faces
        boxes, _ = mtcnn.detect(image)

        faces = []
        if boxes is not None:
            for i, box in enumerate(boxes):
                box = [int(b) for b in box]
                face = image[box[1] : box[3], box[0] : box[2]]
                faces.append(cv2.cvtColor(face, cv2.COLOR_RGB2BGR))
        return faces

    def similar_face(self, faces):
        # Define the transformations
        transform = transforms.Compose(
            [
                transforms.Resize(
                    (342, 342), interpolation=transforms.InterpolationMode.BILINEAR
                ),
                transforms.CenterCrop(299),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

        results = []
        largest_face = None
        largest_area = 0

        input_images = [transform(Image.fromarray(face)).unsqueeze(0) for face in faces]
        for i, input_image in enumerate(input_images):
            input_image = input_image.to("cuda" if torch.cuda.is_available() else "cpu")

            # 입력 이미지에 대한 연예인 얼굴 예측
            with torch.no_grad():
                self.model.eval()
                outputs = self.model(input_image)
                predictions = torch.exp(outputs)
            
            _, predict_class_index = torch.max(predictions, 1)
            predict_label = self.class_labels[predict_class_index]
            print(predict_label, predictions)
        
            c_result = [
                predict_label,
                round(predictions[0][predict_class_index].item() * 100, 2),
            ]

            results.append([c_result, faces[i]])

            # Check if this face is the largest
            face_area = faces[i].shape[0] * faces[i].shape[1]
            if face_area > largest_area:
                largest_area = face_area
                largest_face = faces[i]

        img = Image.fromarray(largest_face)
        rawBytes = io.BytesIO()
        img.save(rawBytes, "PNG")
        rawBytes.seek(0)
        img_base64 = base64.b64encode(rawBytes.read())

        print(largest_area, largest_face.shape)

        return [max(results, key=lambda x: x[0][1]), img_base64.decode("utf-8")]

    def analyze(self):
        image = self.read_image()
        faces = self.face_extraction(image)
        if not faces:
            raise ValueError("얼굴을 찾을 수 없습니다.")
        return self.similar_face(faces)

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
