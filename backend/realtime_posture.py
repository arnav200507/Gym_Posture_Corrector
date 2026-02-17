"""
realtime_posture.py
Real-time squat posture analyser with side dashboard UI and session logging.
"""

import cv2
import json
import numpy as np
from pose_detector import detect_pose
from angle_utils import calculate_angle

LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27

SQUAT_CORRECT_LOW = 70
SQUAT_CORRECT_HIGH = 100
STANDING_THRESHOLD = 160


def save_session_stats(reps):
    data = {"total_reps": reps}
    with open("session_stats.json", "w") as f:
        json.dump(data, f)


def draw_dashboard(frame, knee_angle, posture, reps, stage):
    h, w, _ = frame.shape
    panel_width = 350

    dashboard = np.zeros((h, w + panel_width, 3), dtype=np.uint8)
    dashboard[:, :w] = frame

    cv2.rectangle(dashboard, (w, 0), (w + panel_width, h), (25, 25, 25), -1)

    white = (255, 255, 255)
    green = (0, 255, 120)
    red = (0, 0, 255)
    yellow = (255, 220, 0)

    posture_color = green if posture == "Correct" else red

    # Suggestion logic
    if posture == "Incorrect":
        suggestion = "Go lower / bend knees more"
    else:
        suggestion = "Good posture"

    cv2.putText(dashboard, "POSTURE DASHBOARD", (w + 20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, white, 2)

    cv2.putText(dashboard, f"Knee Angle: {knee_angle:.1f}", (w + 20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, white, 2)

    cv2.putText(dashboard, f"Posture: {posture}", (w + 20, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, posture_color, 2)

    cv2.putText(dashboard, f"Reps: {reps}", (w + 20, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, white, 2)

    cv2.putText(dashboard, f"Stage: {stage}", (w + 20, 270),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, white, 2)

    cv2.putText(dashboard, "Suggestion:", (w + 20, 340),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, white, 2)

    cv2.putText(dashboard, suggestion, (w + 20, 390),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, yellow, 2)

    return dashboard


def draw_landmarks(frame, landmarks):
    joints = [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE]
    points = [(landmarks[j]["x"], landmarks[j]["y"]) for j in joints]

    for i in range(len(points) - 1):
        cv2.line(frame, points[i], points[i + 1], (0, 255, 255), 3)

    for pt in points:
        cv2.circle(frame, pt, 7, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, pt, 9, (255, 255, 255), 2)


def main():
    cap = cv2.VideoCapture(0)

    reps = 0
    stage = "up"

    cv2.namedWindow("Gym Posture Corrector", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Gym Posture Corrector",
                          cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        landmarks = detect_pose(frame)

        knee_angle = 0
        posture = "No Person"

        if landmarks is not None:
            hip = [landmarks[LEFT_HIP]["x"], landmarks[LEFT_HIP]["y"]]
            knee = [landmarks[LEFT_KNEE]["x"], landmarks[LEFT_KNEE]["y"]]
            ankle = [landmarks[LEFT_ANKLE]["x"], landmarks[LEFT_ANKLE]["y"]]

            knee_angle = calculate_angle(hip, knee, ankle)

            posture = "Correct" if SQUAT_CORRECT_LOW <= knee_angle <= SQUAT_CORRECT_HIGH else "Incorrect"

            if knee_angle <= SQUAT_CORRECT_HIGH:
                stage = "down"

            if knee_angle >= STANDING_THRESHOLD and stage == "down":
                stage = "up"
                reps += 1

            draw_landmarks(frame, landmarks)

        display_frame = draw_dashboard(frame, knee_angle, posture, reps, stage)

        cv2.imshow("Gym Posture Corrector", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    save_session_stats(reps)
    print(f"Session finished. Total reps: {reps}")


if __name__ == "__main__":
    main()
