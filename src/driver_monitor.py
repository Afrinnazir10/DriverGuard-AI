import cv2
import math

try:
    from src.face_detector import FaceDetector
except ImportError:
    from face_detector import FaceDetector


MODEL_PATH = "models/face_landmarker.task"


# =========================================================
# DISTANCE BETWEEN TWO LANDMARKS
# =========================================================

def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


# =========================================================
# EYE ASPECT RATIO
# =========================================================

def calculate_ear(landmarks, eye):

    p1 = landmarks[eye[0]]
    p2 = landmarks[eye[1]]
    p3 = landmarks[eye[2]]
    p4 = landmarks[eye[3]]
    p5 = landmarks[eye[4]]
    p6 = landmarks[eye[5]]

    vertical_1 = distance(p2, p6)
    vertical_2 = distance(p3, p5)

    horizontal = distance(p1, p4)

    if horizontal == 0:
        return 0

    return (vertical_1 + vertical_2) / (2 * horizontal)


# =========================================================
# MOUTH RATIO
# =========================================================

def calculate_mouth_ratio(landmarks):

    top = landmarks[13]
    bottom = landmarks[14]

    left = landmarks[78]
    right = landmarks[308]

    vertical = distance(top, bottom)
    horizontal = distance(left, right)

    if horizontal == 0:
        return 0

    return vertical / horizontal


# =========================================================
# HEAD DIRECTION
# =========================================================

def calculate_head_direction(landmarks):

    nose = landmarks[1]

    left_face = landmarks[234]
    right_face = landmarks[454]

    forehead = landmarks[10]
    chin = landmarks[152]

    face_width = distance(left_face, right_face)
    face_height = distance(forehead, chin)

    if face_width == 0 or face_height == 0:
        return "UNKNOWN"

    horizontal_position = (
        nose.x - left_face.x
    ) / face_width

    vertical_position = (
        nose.y - forehead.y
    ) / face_height

    if horizontal_position < 0.30:
        horizontal_direction = "LEFT"

    elif horizontal_position > 0.70:
        horizontal_direction = "RIGHT"

    else:
        horizontal_direction = "CENTER"

    if vertical_position < 0.30:
        vertical_direction = "UP"

    elif vertical_position > 0.70:
        vertical_direction = "DOWN"

    else:
        vertical_direction = "CENTER"

    if vertical_direction == "DOWN":
        return "LOOKING DOWN"

    if vertical_direction == "UP":
        return "LOOKING UP"

    if horizontal_direction == "LEFT":
        return "LOOKING LEFT"

    if horizontal_direction == "RIGHT":
        return "LOOKING RIGHT"

    return "FORWARD"


# =========================================================
# DRIVER MONITOR
# =========================================================

class DriverMonitor:

    def __init__(self):

        self.detector = FaceDetector(MODEL_PATH)

        self.LEFT_EYE = [
            33, 160, 158,
            133, 153, 144
        ]

        self.RIGHT_EYE = [
            362, 385, 387,
            263, 373, 380
        ]

        self.closed_eye_frames = 0
        self.yawn_frames = 0
        self.distraction_frames = 0


    # =====================================================
    # PROCESS ONE CAMERA FRAME
    # =====================================================

    def process_frame(self, frame):

        result = self.detector.detect(frame)

        # -------------------------------------------------
        # DEFAULT VALUES
        # -------------------------------------------------

        data = {

            "face_detected": False,

            "ear": 0.0,

            "mouth_ratio": 0.0,

            "driver_status": "NO DRIVER FACE",

            "yawning_status": "NO YAWNING",

            "head_direction": "UNKNOWN",

            "attention_status": "UNKNOWN",

            "safety_status": "UNKNOWN",

            "safety_score": 0

        }


        # -------------------------------------------------
        # NO FACE
        # -------------------------------------------------

        if not result.face_landmarks:

            self.closed_eye_frames = 0
            self.yawn_frames = 0
            self.distraction_frames = 0

            return frame, data


        # -------------------------------------------------
        # FACE FOUND
        # -------------------------------------------------

        data["face_detected"] = True

        landmarks = result.face_landmarks[0]

        h, w, _ = frame.shape


        # =================================================
        # EYE ANALYSIS
        # =================================================

        left_ear = calculate_ear(
            landmarks,
            self.LEFT_EYE
        )

        right_ear = calculate_ear(
            landmarks,
            self.RIGHT_EYE
        )

        ear = (left_ear + right_ear) / 2

        data["ear"] = ear


        if ear < 0.20:

            self.closed_eye_frames += 1

        else:

            self.closed_eye_frames = 0


        # =================================================
        # DROWSINESS
        # =================================================

        if self.closed_eye_frames >= 15:

            driver_status = "CRITICAL DROWSINESS"

        elif self.closed_eye_frames >= 7:

            driver_status = "GETTING DROWSY"

        else:

            driver_status = "DRIVER ALERT"


        data["driver_status"] = driver_status


        # =================================================
        # YAWNING
        # =================================================

        mouth_ratio = calculate_mouth_ratio(
            landmarks
        )

        data["mouth_ratio"] = mouth_ratio


        if mouth_ratio > 0.55:

            self.yawn_frames += 1

        else:

            self.yawn_frames = 0


        if self.yawn_frames >= 5:

            yawning_status = "YAWNING DETECTED"

        else:

            yawning_status = "NO YAWNING"


        data["yawning_status"] = yawning_status


        # =================================================
        # HEAD DIRECTION
        # =================================================

        head_direction = calculate_head_direction(
            landmarks
        )

        data["head_direction"] = head_direction


        # =================================================
        # DISTRACTION
        # =================================================

        if head_direction in [
            "LOOKING LEFT",
            "LOOKING RIGHT",
            "LOOKING DOWN"
        ]:

            self.distraction_frames += 1

        else:

            self.distraction_frames = 0


        if self.distraction_frames >= 15:

            if head_direction == "LOOKING DOWN":

                attention_status = "SEVERE DISTRACTION"

            else:

                attention_status = "DISTRACTED"


        elif self.distraction_frames >= 5:

            attention_status = "GETTING DISTRACTED"


        else:

            attention_status = "FOCUSED"


        data["attention_status"] = attention_status


        # =================================================
        # SAFETY SCORE
        # =================================================

        score = 100


        # Drowsiness penalty

        if driver_status == "GETTING DROWSY":

            score -= 20

        elif driver_status == "CRITICAL DROWSINESS":

            score -= 50


        # Yawning penalty

        if yawning_status == "YAWNING DETECTED":

            score -= 10


        # Distraction penalty

        if attention_status == "GETTING DISTRACTED":

            score -= 15

        elif attention_status == "DISTRACTED":

            score -= 30

        elif attention_status == "SEVERE DISTRACTION":

            score -= 50


        score = max(0, min(100, score))


        data["safety_score"] = score


        # =================================================
        # OVERALL SAFETY STATUS
        # =================================================

        if score >= 80:

            safety_status = "SAFE"

        elif score >= 50:

            safety_status = "CAUTION"

        else:

            safety_status = "HIGH RISK"


        data["safety_status"] = safety_status


        # =================================================
        # DRAW LANDMARKS
        # =================================================

        for landmark in landmarks:

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            cv2.circle(
                frame,
                (x, y),
                1,
                (255, 255, 255),
                -1
            )


        # =================================================
        # DRAW AI INFORMATION
        # =================================================

        cv2.putText(
            frame,
            "DRIVERGUARD AI",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            driver_status,
            (30, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            yawning_status,
            (30, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "ATTENTION: " + attention_status,
            (30, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "HEAD: " + head_direction,
            (30, 205),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        return frame, data


    # =====================================================
    # CLOSE DETECTOR
    # =====================================================

    def close(self):

        self.detector.close()
