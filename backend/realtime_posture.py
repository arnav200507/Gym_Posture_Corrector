"""
realtime_posture.py
===================
Standalone real-time squat posture analyser.
Captures webcam video, detects pose via MediaPipe, calculates the
knee angle, determines squat correctness, counts reps, and overlays
all information on the live video feed.

Press 'q' to quit.
"""

import cv2
import numpy as np
from pose_detector import detect_pose
from angle_utils import calculate_angle

# ── MediaPipe landmark indices ──────────────────────────────────
LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27

# ── Squat thresholds ────────────────────────────────────────────
SQUAT_CORRECT_LOW = 70      # knee angle lower bound for "Correct"
SQUAT_CORRECT_HIGH = 100    # knee angle upper bound for "Correct"
STANDING_THRESHOLD = 160    # angle above which we consider the person standing


def draw_overlay(frame, knee_angle, posture, reps, stage):
    """Draw a translucent info panel on the top-left of the frame."""
    overlay = frame.copy()

    # Semi-transparent dark rectangle
    cv2.rectangle(overlay, (0, 0), (350, 200), (30, 30, 30), cv2.FILLED)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Colours
    green = (0, 230, 118)
    red = (70, 70, 255)
    white = (255, 255, 255)
    cyan = (255, 220, 0)

    posture_colour = green if posture == "Correct" else red

    # Text lines
    cv2.putText(frame, f"Knee Angle: {knee_angle:.1f} deg",
                (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, cyan, 2)
    cv2.putText(frame, f"Posture: {posture}",
                (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.85, posture_colour, 2)
    cv2.putText(frame, f"Reps: {reps}",
                (15, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.85, white, 2)
    cv2.putText(frame, f"Stage: {stage}",
                (15, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.7, white, 2)

    return frame


def draw_landmarks(frame, landmarks):
    """Draw key joint connections on the frame for visual feedback."""
    # Connections to draw: hip → knee → ankle
    joints = [LEFT_HIP, LEFT_KNEE, LEFT_ANKLE]
    points = [(landmarks[j]["x"], landmarks[j]["y"]) for j in joints]

    for i in range(len(points) - 1):
        cv2.line(frame, points[i], points[i + 1], (0, 255, 255), 3)

    for pt in points:
        cv2.circle(frame, pt, 7, (0, 0, 255), cv2.FILLED)
        cv2.circle(frame, pt, 9, (255, 255, 255), 2)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam.")
        return

    reps = 0
    stage = "up"   # "up" = standing, "down" = squatting

    print("Real-time Squat Posture Analyser")
    print("Press 'q' to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Detect pose landmarks
        landmarks = detect_pose(frame)

        if landmarks is None:
            # No person detected — show a message
            cv2.putText(frame, "No person detected",
                        (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 0, 255), 2)
            cv2.imshow("Gym Posture Corrector", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue

        # Extract key joint coordinates
        hip = [landmarks[LEFT_HIP]["x"], landmarks[LEFT_HIP]["y"]]
        knee = [landmarks[LEFT_KNEE]["x"], landmarks[LEFT_KNEE]["y"]]
        ankle = [landmarks[LEFT_ANKLE]["x"], landmarks[LEFT_ANKLE]["y"]]

        # Calculate knee angle
        knee_angle = calculate_angle(hip, knee, ankle)

        # Determine posture
        posture = "Correct" if SQUAT_CORRECT_LOW <= knee_angle <= SQUAT_CORRECT_HIGH else "Incorrect"

        # ── Rep counting logic ──────────────────────────────────
        # DOWN stage: knee angle drops into the correct squat range
        if knee_angle <= SQUAT_CORRECT_HIGH:
            stage = "down"

        # UP stage: knee angle returns above the standing threshold ⇒ 1 rep
        if knee_angle >= STANDING_THRESHOLD and stage == "down":
            stage = "up"
            reps += 1

        # ── Draw visuals ────────────────────────────────────────
        draw_landmarks(frame, landmarks)
        frame = draw_overlay(frame, knee_angle, posture, reps, stage)

        cv2.imshow("Gym Posture Corrector", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nSession finished. Total reps: {reps}")


if __name__ == "__main__":
    main()
