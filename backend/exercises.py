"""
exercises.py
============
Exercise-specific evaluation functions.
Each function takes the landmarks list returned by `detect_pose()`
and returns the computed angle along with a posture verdict.
"""

from angle_utils import calculate_angle

# MediaPipe Pose landmark indices
LEFT_HIP = 23
LEFT_KNEE = 25
LEFT_ANKLE = 27


def evaluate_squat(landmarks: list[dict]) -> dict:
    """
    Evaluate squat form by measuring the knee angle.

    Parameters
    ----------
    landmarks : list[dict]
        List of 33 landmark dicts from ``detect_pose()``, each with
        ``"x"`` and ``"y"`` pixel coordinates.

    Returns
    -------
    dict
        {
            "exercise": "squat",
            "knee_angle": float,       # degrees
            "posture": "Correct" | "Incorrect"
        }
    """
    hip   = [landmarks[LEFT_HIP]["x"],   landmarks[LEFT_HIP]["y"]]
    knee  = [landmarks[LEFT_KNEE]["x"],  landmarks[LEFT_KNEE]["y"]]
    ankle = [landmarks[LEFT_ANKLE]["x"], landmarks[LEFT_ANKLE]["y"]]

    knee_angle = calculate_angle(hip, knee, ankle)

    posture = "Correct" if 70 <= knee_angle <= 100 else "Incorrect"

    return {
        "exercise": "squat",
        "knee_angle": round(knee_angle, 2),
        "posture": posture,
    }
