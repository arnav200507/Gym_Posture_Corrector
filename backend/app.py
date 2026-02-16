"""
Gym Posture Corrector – Backend API
====================================
FastAPI server for real-time posture analysis.
"""

from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np

from pose_detector import detect_pose
from exercises import evaluate_squat

app = FastAPI(title="Gym Posture Corrector API", version="1.0.0")


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "running"}


@app.post("/analyze_frame")
async def analyze_frame(file: UploadFile = File(...)):
    """
    Receive an uploaded image frame, detect pose landmarks,
    evaluate squat posture, and return the result as JSON.
    """
    # Read uploaded file bytes and convert to OpenCV frame
    contents = await file.read()
    np_arr = np.frombuffer(contents, dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Invalid image file"}

    # Detect pose landmarks
    landmarks = detect_pose(frame)

    if landmarks is None:
        return {"error": "No person detected in the frame"}

    # Evaluate squat posture
    result = evaluate_squat(landmarks)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
