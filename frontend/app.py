"""
Gym Posture Corrector – Streamlit Frontend
============================================
A clean, real-time dashboard that captures webcam video, sends frames
to the Flask backend for pose analysis, and displays corrective
feedback along with rep counts.
"""

import streamlit as st
import cv2
import base64
import requests
import numpy as np
from datetime import datetime

# ── Configuration ───────────────────────────────────────────────
BACKEND_URL = "http://localhost:5000"

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
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .metric-card h2 { margin: 0; font-size: 2.2rem; }
    .metric-card p  { margin: 0; opacity: 0.85; }
    .feedback-good {
        background: #d4edda; border-left: 4px solid #28a745;
        padding: 0.6rem 1rem; border-radius: 4px; margin: 0.3rem 0;
    }
    .feedback-warn {
        background: #fff3cd; border-left: 4px solid #ffc107;
        padding: 0.6rem 1rem; border-radius: 4px; margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ─────────────────────────────────────────────────────
def sidebar():
    st.sidebar.image(
        "https://img.icons8.com/emoji/96/000000/person-lifting-weights.png",
        width=80,
    )
    st.sidebar.title("⚙️ Settings")

    # Fetch available exercises
    exercises = ["bicep_curl", "shoulder_press", "squat", "deadlift", "lateral_raise"]
    try:
        resp = requests.get(f"{BACKEND_URL}/exercises", timeout=3)
        if resp.ok:
            exercises = resp.json().get("exercises", exercises)
    except requests.ConnectionError:
        st.sidebar.warning("⚠️ Backend not reachable – using defaults.")

    selected = st.sidebar.selectbox(
        "Exercise",
        exercises,
        format_func=lambda x: x.replace("_", " ").title(),
    )

    if st.sidebar.button("Set Exercise"):
        try:
            requests.post(
                f"{BACKEND_URL}/exercise",
                json={"exercise": selected},
                timeout=3,
            )
            st.sidebar.success(f"Exercise set to **{selected.replace('_',' ').title()}**")
        except requests.ConnectionError:
            st.sidebar.error("Could not reach backend.")

    if st.sidebar.button("🔄 Reset Counters"):
        try:
            requests.post(f"{BACKEND_URL}/reset", timeout=3)
            st.sidebar.info("Counters reset.")
        except requests.ConnectionError:
            st.sidebar.error("Could not reach backend.")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Session started: {datetime.now():%H:%M:%S}")
    return selected


# ── Helpers ─────────────────────────────────────────────────────
def encode_frame(frame: np.ndarray) -> str:
    """Encode an OpenCV BGR frame as a base64 JPEG data-URI."""
    _, buf = cv2.imencode(".jpg", frame)
    b64 = base64.b64encode(buf).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def render_feedback(feedback_list: list[str]):
    """Render feedback messages with styled HTML."""
    for msg in feedback_list:
        css_class = "feedback-good" if "✅" in msg else "feedback-warn"
        st.markdown(f'<div class="{css_class}">{msg}</div>', unsafe_allow_html=True)


# ── Main ────────────────────────────────────────────────────────
def main():
    st.markdown(
        '<div class="main-header"><h1>🏋️ Gym Posture Corrector</h1>'
        "<p>Real-time AI-powered form feedback for your workouts</p></div>",
        unsafe_allow_html=True,
    )

    exercise = sidebar()

    col_video, col_stats = st.columns([3, 1])

    with col_stats:
        st.subheader("📊 Live Stats")
        reps_placeholder = st.empty()
        stage_placeholder = st.empty()
        angle_placeholder = st.empty()
        feedback_placeholder = st.empty()

    with col_video:
        run = st.checkbox("▶️  Start Camera", value=False)
        frame_display = st.empty()

    if run:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Cannot access webcam. Check your camera settings.")
            return

        while run:
            ret, frame = cap.read()
            if not ret:
                st.warning("Frame capture failed.")
                break

            # Send frame to backend
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/analyze",
                    json={"frame": encode_frame(frame)},
                    timeout=5,
                )
                data = resp.json()
            except Exception as exc:
                frame_display.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True,
                )
                feedback_placeholder.warning(f"Backend error: {exc}")
                continue

            # Show annotated frame
            if data.get("annotated_frame"):
                frame_display.image(
                    data["annotated_frame"],
                    use_container_width=True,
                )
            else:
                frame_display.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    use_container_width=True,
                )

            # Update stats
            reps_placeholder.markdown(
                f'<div class="metric-card"><h2>{data.get("reps", 0)}</h2>'
                f"<p>Reps</p></div>",
                unsafe_allow_html=True,
            )
            stage_placeholder.markdown(
                f'<div class="metric-card"><h2>{(data.get("stage") or "–").upper()}</h2>'
                f"<p>Stage</p></div>",
                unsafe_allow_html=True,
            )

            # Angles
            angles = data.get("angles", {})
            if angles:
                angle_str = " | ".join(
                    f"**{k.replace('_',' ').title()}**: {v}°" for k, v in angles.items()
                )
                angle_placeholder.markdown(angle_str)

            # Feedback
            with feedback_placeholder.container():
                render_feedback(data.get("feedback", []))

        cap.release()
    else:
        st.info("Toggle **Start Camera** to begin real-time analysis.")


if __name__ == "__main__":
    main()
