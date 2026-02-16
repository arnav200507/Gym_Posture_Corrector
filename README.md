# 🏋️ Gym Posture Corrector

Real-time AI-powered posture analysis and corrective feedback for common gym exercises using **MediaPipe Pose** and **OpenCV**.

---

## 📁 Project Structure

```
Gym_Posture_Corrector/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── pose_detector.py    # MediaPipe Pose wrapper
│   ├── angle_utils.py      # Joint-angle math utilities
│   ├── exercises.py        # Exercise catalogue & evaluation logic
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   └── app.py              # Streamlit dashboard
│
└── README.md
```

## ✨ Features

| Feature | Details |
|---|---|
| **Pose Detection** | 33 body landmarks via MediaPipe Pose |
| **Angle Computation** | 3-D joint angles for form evaluation |
| **Rep Counting** | Automatic stage-based repetition tracking |
| **Live Feedback** | Corrective hints displayed in real time |
| **5 Exercises** | Bicep Curl · Shoulder Press · Squat · Deadlift · Lateral Raise |

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
pip install streamlit
```

### 2. Start the backend server

```bash
cd backend
python app.py
```

The API will be available at **http://localhost:5000**.

### 3. Launch the frontend

```bash
cd frontend
streamlit run app.py
```

Open the URL shown in the terminal (usually **http://localhost:8501**).

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Service info |
| `GET`  | `/exercises` | List supported exercises |
| `POST` | `/exercise` | Set active exercise (`{ "exercise": "squat" }`) |
| `POST` | `/analyze` | Send a base64 frame, receive angles + feedback |
| `GET`  | `/stats` | Current rep count and stage |
| `POST` | `/reset` | Reset rep counter |

## 🛠️ Tech Stack

- **Python 3.10+**
- **Flask** – lightweight REST API
- **MediaPipe** – pose landmark detection
- **OpenCV** – image processing
- **Streamlit** – interactive frontend dashboard
- **NumPy** – angle calculations

## 📜 License

This project is for educational purposes.
