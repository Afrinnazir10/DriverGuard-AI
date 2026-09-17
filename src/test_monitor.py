import cv2

from driver_monitor import DriverMonitor


def main():

    monitor = DriverMonitor()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")
        monitor.close()
        return

    print("DriverGuard Monitor Test Started")
    print("Press ESC to exit.")

    while True:

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")
            break

        # Process the frame using our new DriverMonitor
        frame, data = monitor.process_frame(frame)

        # -------------------------------------------------
        # DISPLAY RESULTS
        # -------------------------------------------------

        print(
            f"\r"
            f"Face: {data['face_detected']} | "
            f"Driver: {data['driver_status']} | "
            f"Yawning: {data['yawning_status']} | "
            f"Attention: {data['attention_status']} | "
            f"Head: {data['head_direction']} | "
            f"Score: {data['safety_score']} | "
            f"Safety: {data['safety_status']}",
            end=""
        )

        cv2.imshow(
            "DriverGuard Monitor Test",
            frame
        )

        # ESC key
        if cv2.waitKey(1) & 0xFF == 27:

            break

    camera.release()

    monitor.close()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
