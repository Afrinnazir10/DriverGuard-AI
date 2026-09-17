import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceDetector:

    def __init__(self, model_path):

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True
        )

        self.detector = vision.FaceLandmarker.create_from_options(
            options
        )

        self.timestamp_ms = 0

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        self.timestamp_ms += 33

        result = self.detector.detect_for_video(
            image,
            self.timestamp_ms
        )

        return result

    def close(self):
        self.detector.close()
