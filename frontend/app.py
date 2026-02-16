"""
Gym Posture Corrector – Streamlit Frontend
============================================
Opens webcam, streams frames to the FastAPI backend /analyze_frame
endpoint, and displays knee angle + posture verdict in real time.
"""

import streamlit as st
import cv2
import requests
import numpy as np

# ── Configuration ───────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Gym Posture Corrector",
    page_icon="🏋️",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
    }
    .main-header h1 { font-size: 2.4rem; margin-bottom: 0.2rem; }
    .main-header p  { opacity: 0.7; font-size: 1.1rem; }

    .metric-card {
        border-radius: 14px;
        padding: 1.4rem 1rem;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .metric-card h2 { margin: 0; font-size: 2.6rem; font-weight: 700; }
    .metric-card p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem; }

    .card-angle    { background: linear-gradient(135deg, #667eea, #764ba2); }
    .card-correct  { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .card-incorrect{ background: linear-gradient(135deg, #eb3349, #f45c43); }
    .card-no-pose  { background: linear-gradient(135deg, #636e72, #b2bec3); }
</style>
""", unsafe_allow_html=True)


# ── Main ────────────────────────────────────────────────────────
def main():
    st.markdown(
        '<div class="main-header">'
        "<h1>🏋️ Gym Posture Corrector</h1>"
        "<p>Real-time AI-powered squat form feedback</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    col_video, col_stats = st.columns([3, 1])

    with col_stats:
        st.subheader("📊 Live Stats")
        angle_placeholder = st.empty()
        posture_placeholder = st.empty()
        info_placeholder = st.empty()

    with col_video:
        run = st.checkbox("▶️  Start Camera", value=False)
        frame_display = st.empty()

    if not run:
        st.info("Toggle **Start Camera** above to begin real-time analysis.")
        return

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Cannot access webcam. Check your camera settings.")
        return

    while run:
        ret, frame = cap.read()
        if not ret:
            st.warning("Frame capture failed — retrying …")
            continue

        # Encode frame as JPEG bytes for upload
        success, buf = cv2.imencode(".jpg", frame)
        if not success:
            continue

        # Send to backend /analyze_frame as a file upload
        try:
            resp = requests.post(
                f"{BACKEND_URL}/analyze_frame",
                files={"file": ("frame.jpg", buf.tobytes(), "image/jpeg")},
                timeout=5,
            )
            data = resp.json()
        except Exception as exc:
            # Show raw frame and an error message
            frame_display.image(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                channels="RGB",
                use_container_width=True,
            )
            info_placeholder.warning(f"⚠️ Backend error: {exc}")
            continue

        # ── Display the webcam frame ─────────────────────────────
        frame_display.image(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            channels="RGB",
            use_container_width=True,
        )

        # ── Handle errors from backend ───────────────────────────
        if "error" in data:
            angle_placeholder.markdown(
                '<div class="metric-card card-no-pose">'
                "<h2>—</h2><p>Knee Angle</p></div>",
                unsafe_allow_html=True,
            )
            posture_placeholder.markdown(
                '<div class="metric-card card-no-pose">'
                "<h2>—</h2><p>Posture</p></div>",
                unsafe_allow_html=True,
            )
            info_placeholder.info(f"ℹ️ {data['error']}")
            continue

        # ── Update live metrics ──────────────────────────────────
        knee_angle = data.get("knee_angle", "—")
        posture = data.get("posture", "—")

        # Knee angle card
        angle_placeholder.markdown(
            f'<div class="metric-card card-angle">'
            f"<h2>{knee_angle}°</h2><p>Knee Angle</p></div>",
            unsafe_allow_html=True,
        )

        # Posture card (green = correct, red = incorrect)
        if posture == "Correct":
            card_cls = "card-correct"
            icon = "✅"
        else:
            card_cls = "card-incorrect"
            icon = "❌"

        posture_placeholder.markdown(
            f'<div class="metric-card {card_cls}">'
            f"<h2>{icon} {posture}</h2><p>Posture</p></div>",
            unsafe_allow_html=True,
        )

        info_placeholder.empty()

    cap.release()


if __name__ == "__main__":
    main()
