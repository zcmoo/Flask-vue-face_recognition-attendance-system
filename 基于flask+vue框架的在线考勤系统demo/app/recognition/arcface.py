import os
import pickle
from keras.applications.imagenet_utils import preprocess_input
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))  
from app.recognition.utils.anchors import Anchors
from app.recognition.utils.config import cfg_mnet, cfg_re50
from app.recognition.utils.utils import (Alignment_1, BBoxUtility, letterbox_image, retinaface_correct_boxes, cv2ImgAddText, compare_faces)
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from app.models_kq.user import Employee_KQ
from app import db 

class ExtractEmbeddings(object):
    _defaults = {
        "retinaface_model_path": os.path.join(os.path.dirname(__file__), 'model_data', 'retinaface_mobilenet025.h5'),
        "retinaface_backbone": "mobilenet",
        "confidence": 0.9,
        "nms_iou": 0.3,
        "retinaface_input_shape": [320,320,3],
        "letterbox_image": True,
        "arcface_model_path": os.path.join(os.path.dirname(__file__), 'model_data', 'arcface_mobilenet_v1.h5'),
        "arcface_backbone": "mobilenetv1",
        "arcface_input_shape": [112,112,3],
        "arcface_threhold" : 1.0, 
        "embeddings_path" : os.path.join(os.path.dirname(__file__), 'models', 'embeddings.pickle'),
        "names_path" : os.path.join(os.path.dirname(__file__), 'models', 'names.pickle'),
    }
    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)
        if self.retinaface_backbone == "mobilenet":
            self.cfg = cfg_mnet
        else:
            self.cfg = cfg_re50
        self.bbox_util = BBoxUtility(nms_thresh=self.nms_iou)
        self.anchors = Anchors(self.cfg, image_size=(self.retinaface_input_shape[0], self.retinaface_input_shape[1])).get_anchors()
        self.graph = tf.get_default_graph()
        if not os.path.exists(self.embeddings_path):
            with open(self.embeddings_path, "wb") as f:
                pickle.dump([], f)
        if not os.path.exists(self.names_path):
            with open(self.names_path, "wb") as f:
                pickle.dump([], f)
        self.all_face_encodings = pickle.load(open(self.embeddings_path, 'rb'))
        self.all_names = pickle.load(open(self.names_path, 'rb'))
        self.generate()

    def generate(self):
        try:
            from app.recognition.nets_retinaface.retinaface import RetinaFace
            with self.graph.as_default():
                self.retinaface = RetinaFace(self.cfg, self.retinaface_backbone)
                self.retinaface.load_weights(self.retinaface_model_path, by_name=True)
        except Exception as e:
            print(e)
        try:
            from app.recognition.nets_arcface.arcface import arcface
            with self.graph.as_default():
                self.arcface = arcface(self.arcface_input_shape, backbone=self.arcface_backbone, mode="predict")
                self.arcface.load_weights(self.arcface_model_path, by_name=True)
        except Exception as e:
            print(e)

    def encode_face_dataset(self, image_path, name):
        image = np.array(Image.open(image_path), np.float32)
        old_image = image.copy()
        im_height, im_width, _ = np.shape(image)
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
            ]
        if self.letterbox_image:
            image = letterbox_image(image, [self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
        photo = np.expand_dims(preprocess_input(image), 0)
        try:
            with self.graph.as_default():
                preds = self.retinaface.predict(photo)
        except Exception as e:
            print(e)
        results = self.bbox_util.detection_out(preds, anchors, confidence_threshold=self.confidence)
        if len(results) <= 0:
            print(f"工号为{name}的照片中发现无效人脸，请重新拍照")
            return
        results = np.array(results)
        areas = (results[:, 2] - results[:, 0]) * (results[:, 3] - results[:, 1])
        max_index = np.argmax(areas)
        if self.letterbox_image:
            results = retinaface_correct_boxes(results, np.array(
                (self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))
        results[:, :4] = results[:, :4] * scale
        results[:, 5:] = results[:, 5:] * scale_for_landmarks
        result = np.maximum(results[max_index], 0)
        crop_img = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
        landmark = np.reshape(result[5:], (5, 2)) - np.array([int(result[0]), int(result[1])])
        crop_img, _ = Alignment_1(crop_img, landmark)
        crop_img = np.array(
            letterbox_image(np.uint8(crop_img), (self.arcface_input_shape[1], self.arcface_input_shape[0]))) / 255
        crop_img = np.expand_dims(crop_img, 0)
        try:
            with self.graph.as_default():
                face_encoding = self.arcface.predict(crop_img)[0]
        except Exception as e:
            print(e)
        self.all_face_encodings.append(face_encoding)
        self.all_names.append(name)
        with open(self.embeddings_path, "wb") as f:
            f.write(pickle.dumps(self.all_face_encodings))
        with open(self.names_path, "wb") as f:
            f.write(pickle.dumps(self.all_names))

    def detect_image(self, image):
        old_image = image.copy()
        image = np.array(image, np.float32)
        im_height, im_width, _ = np.shape(image)
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]
        if self.letterbox_image:
            image = letterbox_image(image, [self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
        photo = np.expand_dims(preprocess_input(image), 0)
        try:
            with self.graph.as_default():
                preds = self.retinaface.predict(photo)
            results = self.bbox_util.detection_out(preds, anchors, confidence_threshold=self.confidence)
            if len(results) <= 0:
                return {"image": old_image, "name": "unknown"}  
            results = np.array(results)
            areas = (results[:, 2] - results[:, 0]) * (results[:, 3] - results[:, 1])
            max_index = np.argmax(areas)
            if self.letterbox_image:
                results = retinaface_correct_boxes(results, np.array(
                    (self.retinaface_input_shape[0], self.retinaface_input_shape[1])),
                                                    np.array([im_height, im_width]))
            results[:, :4] = results[:, :4] * scale
            results[:, 5:] = results[:, 5:] * scale_for_landmarks
            result = np.maximum(results[max_index], 0)
            crop_img = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
            landmark = np.reshape(result[5:], (5, 2)) - np.array([int(result[0]), int(result[1])])
            crop_img, _ = Alignment_1(crop_img, landmark)
            crop_img = np.array(
                letterbox_image(np.uint8(crop_img),
                                    (self.arcface_input_shape[1], self.arcface_input_shape[0]))) / 255
            crop_img = np.expand_dims(crop_img, 0)
            with self.graph.as_default():
                face_encoding = self.arcface.predict(crop_img)[0]
            matches, face_distances = compare_faces(self.all_face_encodings, face_encoding, tolerance = self.arcface_threhold)
            name = "unknown"
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.all_names[best_match_index]
            result = list(map(int, result))
            cv2.rectangle(old_image, (result[0], result[1]), (result[2], result[3]), (0, 0, 255), 2)
            employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == name).first()
            if employee:
                old_image = cv2ImgAddText(old_image, str(employee.employee_name), result[0] + 5, result[3] - 25)
            else:
                old_image = cv2ImgAddText(old_image, "unknown", result[0] + 5, result[3] - 25)
            return {"image": old_image, "name": name}
        except Exception as e:
            print(e)


    def draw_face_frame(self, image):
        old_image = image.copy()
        image = np.array(image, np.float32)
        im_height, im_width, _ = np.shape(image)
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]
        if self.letterbox_image:
            image = letterbox_image(image, [self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
        photo = np.expand_dims(preprocess_input(image), 0)
        try:
            with self.graph.as_default():
                preds = self.retinaface.predict(photo)
            results = self.bbox_util.detection_out(preds, anchors, confidence_threshold=self.confidence)
            if len(results) <= 0:
                return old_image
            results = np.array(results)
            areas = (results[:, 2] - results[:, 0]) * (results[:, 3] - results[:, 1])
            max_index = np.argmax(areas)
            if self.letterbox_image:
                results = retinaface_correct_boxes(results, np.array(
                    (self.retinaface_input_shape[0], self.retinaface_input_shape[1])),
                                                    np.array([im_height, im_width]))
            results[:, :4] = results[:, :4] * scale
            results[:, 5:] = results[:, 5:] * scale_for_landmarks
            result = np.maximum(results[max_index], 0)
            result = list(map(int, result))
            cv2.rectangle(old_image, (result[0], result[1]), (result[2], result[3]), (0, 0, 255), 2)
            return old_image
        except Exception as e:
            print(e)


    def encode_face_dataset_visualization(self, image_path):
        image = np.array(Image.open(image_path), np.float32)
        old_image = image.copy()
        im_height, im_width, _ = np.shape(image)
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
            ]
        if self.letterbox_image:
            image = letterbox_image(image, [self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
        photo = np.expand_dims(preprocess_input(image), 0)
        try:
            with self.graph.as_default():
                preds = self.retinaface.predict(photo)
        except Exception as e:
            print(e)
        results = self.bbox_util.detection_out(preds, anchors, confidence_threshold=self.confidence)
        if len(results) <= 0:
            return
        results = np.array(results)
        areas = (results[:, 2] - results[:, 0]) * (results[:, 3] - results[:, 1])
        max_index = np.argmax(areas)
        if self.letterbox_image:
            results = retinaface_correct_boxes(results, np.array(
                (self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))
        results[:, :4] = results[:, :4] * scale
        results[:, 5:] = results[:, 5:] * scale_for_landmarks
        result = np.maximum(results[max_index], 0)
        crop_img = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
        landmark = np.reshape(result[5:], (5, 2)) - np.array([int(result[0]), int(result[1])])
        crop_img, _ = Alignment_1(crop_img, landmark)
        crop_img = np.array(
            letterbox_image(np.uint8(crop_img), (self.arcface_input_shape[1], self.arcface_input_shape[0]))) / 255
        crop_img = np.expand_dims(crop_img, 0)
        try:
            with self.graph.as_default():
                face_encoding = self.arcface.predict(crop_img)
        except Exception as e:
            print(e)
        return face_encoding