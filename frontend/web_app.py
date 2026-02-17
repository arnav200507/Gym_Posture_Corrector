import sys
import os

# Allow frontend to access backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
from pose_detector import detect_pose
from angle_utils import calculate_angle

LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27

SQUAT_CORRECT_LOW = 70
SQUAT_CORRECT_HIGH = 100
STANDING_THRESHOLD = 160


class PostureTransformer(VideoTransformerBase):

    def __init__(self):
        self.reps = 0
        self.stage = "up"

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        landmarks = detect_pose(img)

        if landmarks is not None:
            hip = [landmarks[LEFT_HIP]["x"], landmarks[LEFT_HIP]["y"]]
            knee = [landmarks[LEFT_KNEE]["x"], landmarks[LEFT_KNEE]["y"]]
            ankle = [landmarks[LEFT_ANKLE]["x"], landmarks[LEFT_ANKLE]["y"]]

            knee_angle = calculate_angle(hip, knee, ankle)

            posture = "Correct" if SQUAT_CORRECT_LOW <= knee_angle <= SQUAT_CORRECT_HIGH else "Incorrect"

            if knee_angle <= SQUAT_CORRECT_HIGH:
                self.stage = "down"

            if knee_angle >= STANDING_THRESHOLD and self.stage == "down":
                self.stage = "up"
                self.reps += 1

            cv2.putText(img, f"Knee Angle: {knee_angle:.1f}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            cv2.putText(img, f"Reps: {self.reps}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.putText(img, f"Posture: {posture}", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0) if posture == "Correct" else (0, 0, 255), 2)

        return img


# Streamlit UI
st.set_page_config(layout="wide")
st.title("🏋️ Gym Posture Corrector")

st.markdown("Real-time squat posture detection using computer vision.")

webrtc_streamer(
    key="posture",
    video_transformer_factory=PostureTransformer
)
