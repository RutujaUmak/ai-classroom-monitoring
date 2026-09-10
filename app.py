import os
import tempfile
from datetime import datetime

import streamlit as st
import pandas as pd

try:
    import cv2
except Exception as e:
    st.error(f"OpenCV loading failed: {e}")
    st.stop()

from ultralytics import YOLO




import os
import tempfile
from datetime import datetime

import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Classroom Monitoring",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# SAFE OPENCV IMPORT
# ---------------------------------------------------------
try:
    import cv2
except Exception:
    st.error(
        "OpenCV could not be loaded. "
        "Please use 'opencv-python-headless' in requirements.txt."
    )
    st.stop()

# ---------------------------------------------------------
# YOLO IMPORT
# ---------------------------------------------------------
try:
    from ultralytics import YOLO
except Exception as e:
    st.error(f"Ultralytics could not be loaded: {e}")
    st.stop()


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .brand-title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .brand-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .metric-title {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }

    .status-box {
        padding: 15px;
        border-radius: 12px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .alert-box {
        padding: 15px;
        border-radius: 12px;
        background: #fff7ed;
        border-left: 5px solid #f97316;
        margin-bottom: 10px;
    }

    .success-box {
        padding: 15px;
        border-radius: 12px;
        background: #f0fdf4;
        border-left: 5px solid #22c55e;
        margin-bottom: 10px;
    }

    .info-box {
        padding: 15px;
        border-radius: 12px;
        background: #eff6ff;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None

    try:
        return YOLO(MODEL_PATH)
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None


model = load_model()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = pd.DataFrame()

if "total_frames" not in st.session_state:
    st.session_state.total_frames = 0

if "processed_frames" not in st.session_state:
    st.session_state.processed_frames = 0

if "total_detections" not in st.session_state:
    st.session_state.total_detections = 0

if "last_video" not in st.session_state:
    st.session_state.last_video = None


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center;">
            <div style="font-size:45px;">🎓</div>
            <h2>ClassVision AI</h2>
            <p style="color:#9ca3af;">Intelligent Classroom Monitoring</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🎥 Video Analysis",
            "📊 Analytics",
            "🚨 Alerts",
            "⚙️ System"
        ]
    )

    st.divider()

    st.caption("AI Classroom Monitoring")
    st.caption("YOLO-powered computer vision")
    st.caption("Version 1.0")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    '<div class="brand-title">AI Classroom Monitoring</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="brand-subtitle">'
    'Computer vision based classroom activity monitoring system'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":

    st.subheader("Dashboard Overview")

    if model is None:
        st.error(
            "⚠️ `best.pt` was not found in the project folder."
        )

        st.info(
            "Place your trained YOLO model named `best.pt` "
            "in the same folder as `app.py`."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-title">Model Status</div>
                <div class="metric-value">🟢 Ready</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Frames Processed</div>
                <div class="metric-value">
                    {st.session_state.processed_frames}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Detections</div>
                <div class="metric-value">
                    {st.session_state.total_detections}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        alerts = 0

        if not st.session_state.analysis_results.empty:
            alerts = int(
                st.session_state.analysis_results[
                    "Alert"
                ].sum()
            )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Alerts</div>
                <div class="metric-value">
                    {alerts}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    left, right = st.columns([2, 1])

    with left:

        st.markdown("### How the system works")

        st.markdown(
            """
            <div class="info-box">
            <b>1. Upload Classroom Video</b><br>
            Upload a classroom recording for analysis.
            </div>

            <div class="info-box">
            <b>2. AI Detection</b><br>
            YOLO analyzes classroom frames and detects
            objects/classes learned by your trained model.
            </div>

            <div class="info-box">
            <b>3. Activity Analysis</b><br>
            Detection results are converted into structured
            analytics and monitoring information.
            </div>

            <div class="info-box">
            <b>4. Alerts</b><br>
            The system highlights frames with unusually
            high detection activity.
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:

        st.markdown("### Model Information")

        if model is not None:

            names = model.names

            if isinstance(names, dict):
                class_names = list(names.values())
            else:
                class_names = list(names)

            st.markdown(
                f"""
                <div class="status-box">
                <b>Model:</b> best.pt<br><br>
                <b>Classes:</b> {len(class_names)}
                </div>
                """,
                unsafe_allow_html=True
            )

            for name in class_names[:10]:
                st.write(f"• {name}")

            if len(class_names) > 10:
                st.caption(
                    f"+ {len(class_names) - 10} more classes"
                )


# =========================================================
# VIDEO ANALYSIS
# =========================================================
elif page == "🎥 Video Analysis":

    st.subheader("Classroom Video Analysis")

    if model is None:
        st.error(
            "YOLO model `best.pt` is not available."
        )
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        confidence = st.slider(
            "Detection Confidence",
            min_value=0.10,
            max_value=0.95,
            value=0.40,
            step=0.05
        )

    with col2:
        process_every = st.slider(
            "Process Every Nth Frame",
            min_value=1,
            max_value=10,
            value=2
        )

    uploaded_video = st.file_uploader(
        "Upload classroom video",
        type=["mp4", "avi", "mov", "mkv"],
        help="Upload a classroom video for YOLO analysis."
    )

    if uploaded_video is not None:

        st.video(uploaded_video)

        st.write("")

        analyze = st.button(
            "🚀 Start AI Analysis",
            type="primary",
            use_container_width=True
        )

        if analyze:

            progress = st.progress(0)
            status = st.empty()

            temp_input = None
            temp_output = None

            try:

                # -----------------------------------------
                # SAVE INPUT VIDEO
                # -----------------------------------------
                input_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=os.path.splitext(
                        uploaded_video.name
                    )[1]
                )

                input_file.write(
                    uploaded_video.getbuffer()
                )

                input_file.close()

                temp_input = input_file.name

                # -----------------------------------------
                # OPEN VIDEO
                # -----------------------------------------
                cap = cv2.VideoCapture(temp_input)

                if not cap.isOpened():
                    st.error(
                        "Unable to open the uploaded video."
                    )
                    st.stop()

                fps = cap.get(
                    cv2.CAP_PROP_FPS
                )

                if fps <= 0:
                    fps = 25

                width = int(
                    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                )

                height = int(
                    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                )

                total_frames = int(
                    cap.get(cv2.CAP_PROP_FRAME_COUNT)
                )

                # -----------------------------------------
                # OUTPUT FILE
                # -----------------------------------------
                output_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )

                output_file.close()

                temp_output = output_file.name

                fourcc = cv2.VideoWriter_fourcc(
                    *"mp4v"
                )

                writer = cv2.VideoWriter(
                    temp_output,
                    fourcc,
                    fps,
                    (width, height)
                )

                frame_number = 0
                processed_frames = 0
                total_detections = 0

                records = []

                class_names = model.names

                status.info(
                    "AI is analyzing the classroom video..."
                )

                while True:

                    ret, frame = cap.read()

                    if not ret:
                        break

                    frame_number += 1

                    annotated_frame = frame.copy()

                    # -------------------------------------
                    # PROCESS SELECTED FRAMES
                    # -------------------------------------
                    if frame_number % process_every == 0:

                        results = model.predict(
                            source=frame,
                            conf=confidence,
                            verbose=False
                        )

                        processed_frames += 1

                        detection_count = 0
                        detected_classes = []

                        for result in results:

                            boxes = result.boxes

                            if boxes is None:
                                continue

                            detection_count += len(boxes)

                            for box in boxes:

                                cls_id = int(
                                    box.cls[0]
                                )

                                conf_score = float(
                                    box.conf[0]
                                )

                                if isinstance(
                                    class_names, dict
                                ):
                                    class_name = class_names.get(
                                        cls_id,
                                        str(cls_id)
                                    )
                                else:
                                    class_name = class_names[
                                        cls_id
                                    ]

                                detected_classes.append(
                                    class_name
                                )

                                total_detections += 1

                        # ---------------------------------
                        # ALERT LOGIC
                        # ---------------------------------
                        alert = (
                            detection_count >= 10
                        )

                        records.append(
                            {
                                "Frame": frame_number,
                                "Time (sec)": round(
                                    frame_number / fps,
                                    2
                                ),
                                "Detections": detection_count,
                                "Classes": ", ".join(
                                    sorted(
                                        set(
                                            detected_classes
                                        )
                                    )
                                ),
                                "Alert": alert
                            }
                        )

                        # ---------------------------------
                        # DRAW YOLO RESULTS
                        # ---------------------------------
                        for result in results:

                            annotated_frame = (
                                result.plot()
                            )

                    writer.write(
                        annotated_frame
                    )

                    if total_frames > 0:

                        progress_value = min(
                            frame_number / total_frames,
                            1.0
                        )

                        progress.progress(
                            progress_value
                        )

                cap.release()
                writer.release()

                # -----------------------------------------
                # SAVE RESULTS
                # -----------------------------------------
                results_df = pd.DataFrame(
                    records
                )

                st.session_state.analysis_results = (
                    results_df
                )

                st.session_state.total_frames = (
                    total_frames
                )

                st.session_state.processed_frames = (
                    processed_frames
                )

                st.session_state.total_detections = (
                    total_detections
                )

                st.session_state.last_video = (
                    temp_output
                )

                progress.progress(1.0)

                status.success(
                    "✅ Video analysis completed successfully."
                )

                # -----------------------------------------
                # RESULTS
                # -----------------------------------------
                st.divider()

                st.subheader(
                    "Analysis Results"
                )

                c1, c2, c3, c4 = st.columns(4)

                alert_count = 0

                if not results_df.empty:
                    alert_count = int(
                        results_df["Alert"].sum()
                    )

                with c1:
                    st.metric(
                        "Total Frames",
                        total_frames
                    )

                with c2:
                    st.metric(
                        "Processed Frames",
                        processed_frames
                    )

                with c3:
                    st.metric(
                        "Total Detections",
                        total_detections
                    )

                with c4:
                    st.metric(
                        "Alerts",
                        alert_count
                    )

                # -----------------------------------------
                # OUTPUT VIDEO
                # -----------------------------------------
                st.subheader(
                    "AI Annotated Video"
                )

                if os.path.exists(temp_output):

                    with open(
                        temp_output,
                        "rb"
                    ) as video_file:

                        video_bytes = (
                            video_file.read()
                        )

                    st.video(
                        video_bytes
                    )

                    st.download_button(
                        "⬇️ Download Annotated Video",
                        data=video_bytes,
                        file_name="ai_classroom_analysis.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

                # -----------------------------------------
                # DATA
                # -----------------------------------------
                if not results_df.empty:

                    st.subheader(
                        "Detection Records"
                    )

                    st.dataframe(
                        results_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    csv_data = (
                        results_df.to_csv(
                            index=False
                        ).encode("utf-8")
                    )

                    st.download_button(
                        "⬇️ Download Detection CSV",
                        data=csv_data,
                        file_name="classroom_detection_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            except Exception as e:

                st.error(
                    f"Video processing failed: {e}"
                )

            finally:

                if (
                    temp_input
                    and os.path.exists(temp_input)
                ):
                    try:
                        os.remove(temp_input)
                    except Exception:
                        pass


# =========================================================
# ANALYTICS
# =========================================================
elif page == "📊 Analytics":

    st.subheader("Classroom Analytics")

    df = st.session_state.analysis_results

    if df.empty:

        st.info(
            "No analysis data available yet. "
            "Go to Video Analysis and process a classroom video."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                "### Detection Activity"
            )

            chart_df = df[
                ["Frame", "Detections"]
            ].copy()

            chart_df = chart_df.set_index(
                "Frame"
            )

            st.line_chart(
                chart_df
            )

        with col2:

            st.markdown(
                "### Alert Distribution"
            )

            alert_data = pd.DataFrame(
                {
                    "Status": [
                        "Normal",
                        "Alert"
                    ],
                    "Count": [
                        int(
                            (~df["Alert"]).sum()
                        ),
                        int(
                            df["Alert"].sum()
                        )
                    ]
                }
            )

            st.bar_chart(
                alert_data.set_index(
                    "Status"
                )
            )

        st.divider()

        st.subheader(
            "Performance Summary"
        )

        total_detections = int(
            df["Detections"].sum()
        )

        average_detections = round(
            df["Detections"].mean(),
            2
        )

        maximum_detections = int(
            df["Detections"].max()
        )

        total_alerts = int(
            df["Alert"].sum()
        )

        a, b, c, d = st.columns(4)

        with a:
            st.metric(
                "Total Detections",
                total_detections
            )

        with b:
            st.metric(
                "Average / Frame",
                average_detections
            )

        with c:
            st.metric(
                "Maximum / Frame",
                maximum_detections
            )

        with d:
            st.metric(
                "Alert Frames",
                total_alerts
            )

        st.divider()

        st.subheader(
            "Detected Classes"
        )

        all_classes = []

        for value in df["Classes"].dropna():

            if value:

                all_classes.extend(
                    [
                        x.strip()
                        for x in value.split(",")
                        if x.strip()
                    ]
                )

        if all_classes:

            class_counts = (
                pd.Series(all_classes)
                .value_counts()
                .rename_axis("Class")
                .reset_index(
                    name="Count"
                )
            )

            st.bar_chart(
                class_counts.set_index(
                    "Class"
                )
            )

            st.dataframe(
                class_counts,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No class-level detections recorded."
            )


# =========================================================
# ALERTS
# =========================================================
elif page == "🚨 Alerts":

    st.subheader("Classroom Alerts")

    df = st.session_state.analysis_results

    if df.empty:

        st.info(
            "No alerts available. "
            "Analyze a classroom video first."
        )

    else:

        alerts_df = df[
            df["Alert"] == True
        ].copy()

        if alerts_df.empty:

            st.success(
                "✅ No unusual activity alerts detected."
            )

        else:

            st.warning(
                f"⚠️ {len(alerts_df)} alert frame(s) detected."
            )

            for _, row in alerts_df.iterrows():

                st.markdown(
                    f"""
                    <div class="alert-box">
                    <b>⚠️ Activity Alert</b><br>
                    Frame: {row["Frame"]}<br>
                    Time: {row["Time (sec)"]} seconds<br>
                    Detections: {row["Detections"]}<br>
                    Classes: {row["Classes"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.divider()

            st.subheader(
                "Alert Records"
            )

            st.dataframe(
                alerts_df,
                use_container_width=True,
                hide_index=True
            )

            csv_data = alerts_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Export Alerts",
                data=csv_data,
                file_name="classroom_alerts.csv",
                mime="text/csv",
                use_container_width=True
            )


# =========================================================
# SYSTEM
# =========================================================
elif page == "⚙️ System":

    st.subheader("System Information")

    model_exists = os.path.exists(
        MODEL_PATH
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            "### Model Configuration"
        )

        st.write(
            f"**Model file:** "
            f"{'Available' if model_exists else 'Missing'}"
        )

        if model_exists:
            st.success(
                "best.pt detected"
            )
        else:
            st.error(
                "best.pt not found"
            )

        if model is not None:

            names = model.names

            if isinstance(names, dict):
                number_classes = len(names)
            else:
                number_classes = len(names)

            st.write(
                f"**Number of classes:** "
                f"{number_classes}"
            )

    with col2:

        st.markdown(
            "### Application Status"
        )

        st.write(
            "**Application:** AI Classroom Monitoring"
        )

        st.write(
            "**Framework:** Streamlit"
        )

        st.write(
            "**Computer Vision:** YOLO + OpenCV"
        )

        st.write(
            "**Data Processing:** Pandas"
        )

        st.write(
            f"**Last checked:** "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        )

    st.divider()

    st.subheader(
        "Project Architecture"
    )

    st.code(
        """
AI Classroom Monitoring
│
├── Streamlit Interface
│
├── YOLO Object Detection
│       │
│       └── best.pt
│
├── OpenCV Video Processing
│
├── Detection Analytics
│
├── Alert Generation
│
└── CSV Export
        """,
        language="text"
    )

    st.success(
        "System is configured for classroom video analysis."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "AI Classroom Monitoring • "
    "YOLO Computer Vision • "
    "Streamlit"
)
