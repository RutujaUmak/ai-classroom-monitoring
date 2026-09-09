
import os
import cv2
import tempfile
from datetime import datetime

import pandas as pd
import streamlit as st
from ultralytics import YOLO


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ClassVision AI | Classroom Monitoring",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */
    .stApp {
        background: #f6f8fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Header */
    .hero {
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1e3a8a 100%
        );
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    .hero h1 {
        font-size: 34px;
        margin-bottom: 5px;
    }

    .hero p {
        color: #dbeafe;
        margin: 0;
        font-size: 16px;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 16px;
        padding: 22px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15,23,42,0.05);
        margin-bottom: 18px;
    }

    .card-title {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
    }

    .card-subtitle {
        color: #6b7280;
        font-size: 13px;
    }

    /* Status */
    .status-online {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: #dcfce7;
        color: #166534;
        font-weight: 600;
        font-size: 13px;
    }

    .status-offline {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: #fee2e2;
        color: #991b1b;
        font-weight: 600;
        font-size: 13px;
    }

    /* Alert */
    .alert {
        background: #fff7ed;
        border-left: 5px solid #f97316;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .alert strong {
        color: #9a3412;
    }

    .normal-alert {
        background: #ecfdf5;
        border-left: 5px solid #10b981;
        border-radius: 10px;
        padding: 14px 16px;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 25px 0 5px;
        color: #6b7280;
        font-size: 13px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    /* Hide Streamlit menu */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# MODEL
# ============================================================

@st.cache_resource
def load_model():

    model_path = "best.pt"

    if not os.path.exists(model_path):
        return None

    try:
        return YOLO(model_path)
    except Exception as error:
        st.error(f"Model loading error: {error}")
        return None


model = load_model()


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "analysis_video" not in st.session_state:
    st.session_state.analysis_video = None

if "analysis_summary" not in st.session_state:
    st.session_state.analysis_summary = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:15px 0 25px 0;
        ">
            <div style="font-size:45px;">🎓</div>
            <h2 style="margin:0;">ClassVision AI</h2>
            <p style="color:#9ca3af;">
                Smart Classroom Monitoring
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "MAIN MENU",
        [
            "🏠 Dashboard",
            "📹 Video Analysis",
            "📊 Analytics",
            "🚨 Alerts",
            "⚙️ System"
        ]
    )

    st.markdown("---")

    if model is not None:

        st.markdown(
            '<span class="status-online">● AI Model Online</span>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<span class="status-offline">● Model Not Found</span>',
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div style="
            position:fixed;
            bottom:20px;
            color:#9ca3af;
            font-size:12px;
        ">
        YOLO • OpenCV • Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🎓 ClassVision AI</h1>
        <p>
            Intelligent classroom monitoring powered by
            Computer Vision and YOLO object detection.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.subheader("Dashboard")

    st.caption(
        "Monitor classroom activity and analyze AI detection sessions."
    )

    # --------------------------------------------------------
    # Model status
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "AI Model",
            "Online" if model else "Offline"
        )

    with col2:

        if st.session_state.analysis_summary:

            st.metric(
                "Objects Detected",
                st.session_state.analysis_summary[
                    "total_detections"
                ]
            )

        else:

            st.metric(
                "Objects Detected",
                "—"
            )

    with col3:

        if st.session_state.analysis_summary:

            st.metric(
                "Peak Objects",
                st.session_state.analysis_summary[
                    "peak_objects"
                ]
            )

        else:

            st.metric(
                "Peak Objects",
                "—"
            )

    with col4:

        if st.session_state.analysis_summary:

            st.metric(
                "Frames Processed",
                st.session_state.analysis_summary[
                    "frames_processed"
                ]
            )

        else:

            st.metric(
                "Frames Processed",
                "—"
            )

    st.markdown("")

    # --------------------------------------------------------
    # Quick actions
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    📹 Video Analysis
                </div>
                <div class="card-subtitle">
                    Upload a classroom recording and run
                    YOLO detection on every frame.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Open Video Analysis →",
            use_container_width=True
        ):
            st.info(
                "Select 'Video Analysis' from the sidebar."
            )

    with col2:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    📊 Detection Analytics
                </div>
                <div class="card-subtitle">
                    Review detected objects, peak activity,
                    frame-level results and reports.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "View Analytics →",
            use_container_width=True
        ):
            st.info(
                "Select 'Analytics' from the sidebar."
            )

    # --------------------------------------------------------
    # Recent session
    # --------------------------------------------------------

    st.subheader("Latest Analysis")

    if st.session_state.analysis_summary:

        summary = st.session_state.analysis_summary

        st.success(
            f"Analysis completed at "
            f"{summary['completed_at']}"
        )

        st.write(
            f"**Video:** {summary['video_name']}"
        )

        st.write(
            f"**Duration:** {summary['duration']:.2f} seconds"
        )

    else:

        st.info(
            "No analysis session yet. Upload a classroom "
            "video from the Video Analysis section."
        )


# ============================================================
# VIDEO ANALYSIS
# ============================================================

elif page == "📹 Video Analysis":

    st.subheader("📹 Classroom Video Analysis")

    st.caption(
        "Upload a classroom recording and let the YOLO model "
        "detect objects and activities."
    )

    uploaded_video = st.file_uploader(
        "Upload Classroom Video",
        type=[
            "mp4",
            "avi",
            "mov",
            "mkv"
        ],
        help="Recommended format: MP4"
    )

    if uploaded_video:

        st.success(
            f"✓ Uploaded: {uploaded_video.name}"
        )

        # ----------------------------------------------------
        # Save uploaded video
        # ----------------------------------------------------

        input_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        )

        input_file.write(
            uploaded_video.getbuffer()
        )

        input_file.close()

        # ----------------------------------------------------
        # Video information
        # ----------------------------------------------------

        cap = cv2.VideoCapture(
            input_file.name
        )

        total_frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        if fps <= 0:
            fps = 25

        duration = (
            total_frames / fps
            if fps > 0
            else 0
        )

        cap.release()

        # ----------------------------------------------------
        # Video information cards
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Resolution",
                f"{width} × {height}"
            )

        with col2:
            st.metric(
                "FPS",
                f"{fps:.1f}"
            )

        with col3:
            st.metric(
                "Frames",
                f"{total_frames:,}"
            )

        with col4:
            st.metric(
                "Duration",
                f"{duration:.1f}s"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # Analysis settings
        # ----------------------------------------------------

        st.subheader("⚙️ Analysis Settings")

        col1, col2, col3 = st.columns(3)

        with col1:

            confidence = st.slider(
                "Confidence Threshold",
                min_value=0.10,
                max_value=0.90,
                value=0.40,
                step=0.05
            )

        with col2:

            process_every = st.selectbox(
                "Process Every Nth Frame",
                [1, 2, 3, 5, 10],
                index=0
            )

        with col3:

            max_detections = st.slider(
                "Maximum Detections",
                10,
                100,
                50
            )

        st.markdown("")

        # ----------------------------------------------------
        # Start analysis
        # ----------------------------------------------------

        if st.button(
            "🚀 Start AI Analysis",
            type="primary",
            use_container_width=True
        ):

            if model is None:

                st.error(
                    "best.pt was not found. "
                    "Place your trained model in the same "
                    "folder as app.py."
                )

                st.stop()

            cap = cv2.VideoCapture(
                input_file.name
            )

            if not cap.isOpened():

                st.error(
                    "Unable to open the uploaded video."
                )

                st.stop()

            # ------------------------------------------------
            # Output file
            # ------------------------------------------------

            output_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            output_path = output_file.name

            output_file.close()

            fourcc = cv2.VideoWriter_fourcc(
                *"mp4v"
            )

            writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )

            # ------------------------------------------------
            # UI placeholders
            # ------------------------------------------------

            progress = st.progress(0)

            status_text = st.empty()

            preview = st.empty()

            # ------------------------------------------------
            # Detection records
            # ------------------------------------------------

            records = []

            class_counts = {}

            frame_number = 0

            processed_frames = 0

            total_detections = 0

            peak_objects = 0

            # ------------------------------------------------
            # Process video
            # ------------------------------------------------

            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                # --------------------------------------------
                # Process selected frames
                # --------------------------------------------

                if frame_number % process_every == 0:

                    results = model.predict(
                        frame,
                        conf=confidence,
                        max_det=max_detections,
                        verbose=False
                    )

                    result = results[0]

                    annotated = result.plot()

                    boxes = result.boxes

                    current_count = (
                        len(boxes)
                        if boxes is not None
                        else 0
                    )

                    total_detections += current_count

                    peak_objects = max(
                        peak_objects,
                        current_count
                    )

                    # ----------------------------------------
                    # Class counting
                    # ----------------------------------------

                    if boxes is not None:

                        for cls in boxes.cls:

                            class_id = int(
                                cls.item()
                            )

                            class_name = model.names.get(
                                class_id,
                                str(class_id)
                            )

                            class_counts[class_name] = (
                                class_counts.get(
                                    class_name,
                                    0
                                ) + 1
                            )

                    # ----------------------------------------
                    # Store frame record
                    # ----------------------------------------

                    records.append(
                        {
                            "Frame": frame_number,
                            "Time (sec)": round(
                                frame_number / fps,
                                2
                            ),
                            "Objects Detected": current_count
                        }
                    )

                    processed_frames += 1

                    # ----------------------------------------
                    # Preview
                    # ----------------------------------------

                    rgb_frame = cv2.cvtColor(
                        annotated,
                        cv2.COLOR_BGR2RGB
                    )

                    preview.image(
                        rgb_frame,
                        caption="AI Detection Preview",
                        use_container_width=True
                    )

                    status_text.write(
                        f"Processing frame "
                        f"{frame_number:,} / "
                        f"{total_frames:,} | "
                        f"Objects detected: "
                        f"{current_count}"
                    )

                # --------------------------------------------
                # Write frame
                # --------------------------------------------

                writer.write(
                    annotated
                    if frame_number % process_every == 0
                    else frame
                )

                frame_number += 1

                progress.progress(
                    min(
                        frame_number / total_frames,
                        1.0
                    )
                )

            cap.release()
            writer.release()

            # ------------------------------------------------
            # Create dataframe
            # ------------------------------------------------

            df = pd.DataFrame(records)

            completed_time = datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            )

            summary = {
                "video_name": uploaded_video.name,
                "completed_at": completed_time,
                "duration": duration,
                "frames_processed": processed_frames,
                "total_detections": total_detections,
                "peak_objects": peak_objects,
                "class_counts": class_counts
            }

            st.session_state.analysis_results = df

            st.session_state.analysis_video = output_path

            st.session_state.analysis_summary = summary

            status_text.success(
                "✅ AI analysis completed successfully!"
            )

            st.balloons()

    # --------------------------------------------------------
    # Show latest result
    # --------------------------------------------------------

    if (
        st.session_state.analysis_video
        and st.session_state.analysis_summary
    ):

        st.markdown("---")

        st.subheader(
            "🎥 Analysed Video"
        )

        st.video(
            st.session_state.analysis_video
        )

        with open(
            st.session_state.analysis_video,
            "rb"
        ) as video_file:

            st.download_button(
                "⬇️ Download Analysed Video",
                data=video_file,
                file_name="classvision_analysis.mp4",
                mime="video/mp4",
                use_container_width=True
            )


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📊 Analytics":

    st.subheader("📊 Detection Analytics")

    df = st.session_state.analysis_results

    summary = st.session_state.analysis_summary

    if df is None or summary is None:

        st.info(
            "No analysis data available yet. "
            "Run a video analysis first."
        )

    else:

        # ----------------------------------------------------
        # KPI cards
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Detections",
                f"{summary['total_detections']:,}"
            )

        with col2:

            st.metric(
                "Peak Objects",
                summary["peak_objects"]
            )

        with col3:

            st.metric(
                "Processed Frames",
                f"{summary['frames_processed']:,}"
            )

        with col4:

            st.metric(
                "Video Duration",
                f"{summary['duration']:.1f}s"
            )

        st.markdown("---")

        # ----------------------------------------------------
        # Object count chart
        # ----------------------------------------------------

        st.subheader(
            "📈 Objects Detected Over Time"
        )

        chart_data = df[
            ["Time (sec)", "Objects Detected"]
        ].set_index(
            "Time (sec)"
        )

        st.line_chart(
            chart_data
        )

        # ----------------------------------------------------
        # Class distribution
        # ----------------------------------------------------

        st.subheader(
            "🎯 Detected Classes"
        )

        class_counts = summary[
            "class_counts"
        ]

        if class_counts:

            class_df = pd.DataFrame(
                {
                    "Class": list(
                        class_counts.keys()
                    ),
                    "Detections": list(
                        class_counts.values()
                    )
                }
            ).sort_values(
                "Detections",
                ascending=False
            )

            col1, col2 = st.columns(
                [1, 2]
            )

            with col1:

                st.dataframe(
                    class_df,
                    hide_index=True,
                    use_container_width=True
                )

            with col2:

                st.bar_chart(
                    class_df.set_index(
                        "Class"
                    )
                )

        else:

            st.info(
                "No object classes were detected."
            )

        # ----------------------------------------------------
        # Raw data
        # ----------------------------------------------------

        st.subheader(
            "📋 Frame-Level Detection Data"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # CSV download
        # ----------------------------------------------------

        csv_data = df.to_csv(
            index=False
        )

        st.download_button(
            "⬇️ Download Detection CSV",
            data=csv_data,
            file_name="classroom_detection_report.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# ALERTS
# ============================================================

elif page == "🚨 Alerts":

    st.subheader("🚨 AI Detection Alerts")

    df = st.session_state.analysis_results

    if df is None:

        st.info(
            "Alerts will appear after you analyze a classroom video."
        )

    else:

        # ----------------------------------------------------
        # High activity frames
        # ----------------------------------------------------

        average_objects = (
            df["Objects Detected"].mean()
            if not df.empty
            else 0
        )

        threshold = max(
            average_objects * 1.5,
            3
        )

        alerts = df[
            df["Objects Detected"] >= threshold
        ]

        st.metric(
            "Potential Activity Alerts",
            len(alerts)
        )

        st.caption(
            "Alerts are generated when detected objects "
            "are significantly above the session average."
        )

        st.markdown("---")

        if alerts.empty:

            st.markdown(
                """
                <div class="normal-alert">
                    <strong>✓ No unusual activity detected</strong><br>
                    The analyzed video did not contain frames
                    exceeding the configured activity threshold.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            for _, row in alerts.head(20).iterrows():

                st.markdown(
                    f"""
                    <div class="alert">
                        <strong>⚠️ High Activity Detected</strong><br>
                        Time: {row['Time (sec)']} seconds<br>
                        Objects detected: {row['Objects Detected']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# SYSTEM
# ============================================================

elif page == "⚙️ System":

    st.subheader("⚙️ System Information")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    🤖 AI Model
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if model:

            st.success(
                "YOLO model loaded successfully."
            )

            try:

                model_names = model.names

                st.write(
                    "**Detected Classes:**"
                )

                for class_id, name in model_names.items():

                    st.write(
                        f"• {class_id}: {name}"
                    )

            except Exception:

                st.info(
                    "Class information unavailable."
                )

        else:

            st.error(
                "best.pt not found."
            )

            st.write(
                "Place best.pt in the project root directory."
            )

    with col2:

        st.markdown(
            """
            <div class="card">
                <div class="card-title">
                    💻 Application
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            "**Application:** ClassVision AI"
        )

        st.write(
            "**Framework:** Streamlit"
        )

        st.write(
            "**Computer Vision:** OpenCV"
        )

        st.write(
            "**Object Detection:** YOLO"
        )

        st.write(
            "**Report Format:** CSV"
        )

        st.write(
            "**Status:** Running"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <b>ClassVision AI</b> • AI Classroom Monitoring System<br>
        Built with Streamlit, OpenCV and YOLO
    </div>
    """,
    unsafe_allow_html=True
)
```
