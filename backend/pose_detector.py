"""
pose_detector.py
================
Initializes MediaPipe Pose once at module level and exposes a
`detect_pose(frame)` function that returns landmark pixel coordinates.
"""

import cv2
import mediapipe as mp
import numpy as np

# ── Initialise MediaPipe Pose once ──────────────────────────────
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)


def detect_pose(frame: np.ndarray) -> list[dict] | None:
    """
    Run pose estimation on a BGR OpenCV frame.

    Parameters
    ----------
    frame : np.ndarray
        BGR image from OpenCV (e.g. ``cap.read()``).

    Returns
    -------
    list[dict] | None
        A list of 33 landmark dicts, each containing::

            {
                "id": int,          # landmark index (0-32)
                "name": str,        # e.g. "LEFT_SHOULDER"
                "x": int,           # pixel x
                "y": int,           # pixel y
                "z": float,         # depth (normalised)
                "visibility": float # 0-1 confidence
            }

        Returns ``None`` if no person is detected in the frame.
    """
    h, w, _ = frame.shape

    # MediaPipe expects RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb.flags.writeable = False
    results = pose.process(rgb)

    if results.pose_landmarks is None:
        return None

    landmarks = []
    for idx, lm in enumerate(results.pose_landmarks.landmark):
        landmarks.append({
            "id": idx,
            "name": mp_pose.PoseLandmark(idx).name,
            "x": int(lm.x * w),
            "y": int(lm.y * h),
            "z": round(lm.z, 6),
            "visibility": round(lm.visibility, 4),
        })

    return landmarks
