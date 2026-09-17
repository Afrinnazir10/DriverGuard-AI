import cv2
import math

from face_detector import FaceDetector


MODEL_PATH = "models/face_landmarker.task"


def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


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


def calculate_head_direction(landmarks):

    # Nose
    nose = landmarks[1]

    # Left and right sides of face
    left_face = landmarks[234]
    right_face = landmarks[454]

    # Top and bottom of face
    forehead = landmarks[10]
    chin = landmarks[152]

    face_width = distance(left_face, right_face)
    face_height = distance(forehead, chin)

    if face_width == 0 or face_height == 0:
        return "UNKNOWN"

    # Normalized nose position
    horizontal_position = (
        nose.x - left_face.x
    ) / face_width

    vertical_position = (
        nose.y - forehead.y
    ) / face_height

    # Horizontal head direction
    if horizontal_position < 0.30:

        horizontal_direction = "LEFT"

    elif horizontal_position > 0.70:

        horizontal_direction = "RIGHT"

    else:

        horizontal_direction = "CENTER"

    # Vertical head direction
    if vertical_position < 0.30:

        vertical_direction = "UP"

    elif vertical_position > 0.70:

        vertical_direction = "DOWN"

    else:

        vertical_direction = "CENTER"

    # Combine directions
    if vertical_direction == "DOWN":

        return "LOOKING DOWN"

    if vertical_direction == "UP":

        return "LOOKING UP"

    if horizontal_direction == "LEFT":

        return "LOOKING LEFT"

    if horizontal_direction == "RIGHT":

        return "LOOKING RIGHT"

    return "FORWARD"


def main():

    detector = FaceDetector(MODEL_PATH)

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        return

    print("DriverGuard AI started.")
    print("Press ESC to exit.")

    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380]

    closed_eye_frames = 0
    yawn_frames = 0

    # Distraction history
    distraction_frames = 0

    while True:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")
            break

        result = detector.detect(frame)

        # =================================================
        # FACE DETECTED
        # =================================================

        if result.face_landmarks:

            landmarks = result.face_landmarks[0]

            h, w, _ = frame.shape

            # -------------------------------------------------
            # EYE ANALYSIS
            # -------------------------------------------------

            left_ear = calculate_ear(
                landmarks,
                LEFT_EYE
            )

            right_ear = calculate_ear(
                landmarks,
                RIGHT_EYE
            )

            ear = (left_ear + right_ear) / 2

            if ear < 0.20:

                closed_eye_frames += 1

            else:

                closed_eye_frames = 0

            # -------------------------------------------------
            # DROWSINESS
            # -------------------------------------------------

            if closed_eye_frames >= 15:

                driver_status = "CRITICAL DROWSINESS"
                driver_color = (0, 0, 255)

            elif closed_eye_frames >= 7:

                driver_status = "GETTING DROWSY"
                driver_color = (0, 165, 255)

            else:

                driver_status = "DRIVER ALERT"
                driver_color = (0, 255, 0)

            # -------------------------------------------------
            # YAWNING
            # -------------------------------------------------

            mouth_ratio = calculate_mouth_ratio(
                landmarks
            )

            if mouth_ratio > 0.55:

                yawn_frames += 1

            else:

                yawn_frames = 0

            if yawn_frames >= 5:

                yawning_status = "YAWNING DETECTED"

            else:

                yawning_status = "NO YAWNING"

            # -------------------------------------------------
            # HEAD DIRECTION
            # -------------------------------------------------

            head_direction = calculate_head_direction(
                landmarks
            )

            # -------------------------------------------------
            # DISTRACTION
            # -------------------------------------------------

            if head_direction in [
                "LOOKING LEFT",
                "LOOKING RIGHT",
                "LOOKING DOWN"
            ]:

                distraction_frames += 1

            else:

                distraction_frames = 0

            if distraction_frames >= 15:

                if head_direction == "LOOKING DOWN":

                    attention_status = "SEVERE DISTRACTION"

                else:

                    attention_status = "DISTRACTED"

                attention_color = (0, 0, 255)

            elif distraction_frames >= 5:

                attention_status = "GETTING DISTRACTED"
                attention_color = (0, 165, 255)

            else:

                attention_status = "FOCUSED"
                attention_color = (0, 255, 0)

            # -------------------------------------------------
            # DRAW LANDMARKS
            # -------------------------------------------------

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

            # -------------------------------------------------
            # DISPLAY
            # -------------------------------------------------

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
                driver_color,
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
                attention_color,
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

        # =================================================
        # NO FACE
        # =================================================

        else:

            closed_eye_frames = 0
            yawn_frames = 0
            distraction_frames = 0

            cv2.putText(
                frame,
                "NO DRIVER FACE",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        # =================================================
        # SHOW CAMERA
        # =================================================

        cv2.imshow(
            "DriverGuard AI - Driver Monitoring",
            frame
        )

        if cv2.waitKey(1) & 0xFF == 27:

            break

    camera.release()

    detector.close()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
