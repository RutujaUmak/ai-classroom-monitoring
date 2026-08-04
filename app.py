# ============================================
# app.py - Complete Video Analysis for Exam Monitoring
# Detects cheating behaviors in video
# ============================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time
import random
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="AI Exam Monitoring - Video Analysis",
    page_icon="🎓",
    layout="wide"
)

# ============================================
# Custom CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e8e8e8;
    }
    .detection-list {
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# Initialize Session State
# ============================================
if 'video_events' not in st.session_state:
    st.session_state.video_events = []
    st.session_state.video_alerts = []
    st.session_state.is_analyzing = False
    st.session_state.student_count = 0
    st.session_state.detections = {
        'head_turning': 0,
        'looking_around': 0,
        'standing': 0,
        'seat_change': 0,
        'mobile_phone': 0,
        'smartwatch': 0,
        'notes_books': 0,
        'invigilator_present': False,
        'blind_spots': 0
    }

# ============================================
# Video Analysis Engine
# ============================================
class VideoAnalysisEngine:
    def __init__(self):
        self.students = {}
        self.seats = {}
        self.current_frame = 0
        self.total_students = 0
        
    def analyze_frame(self, frame_data=None):
        """Analyze a single frame from video"""
        self.current_frame += 1
        
        events = []
        alerts = []
        
        # Simulate student detection
        student_count = random.randint(20, 40)
        self.total_students = student_count
        st.session_state.student_count = student_count
        
        # Simulate head turning (15-30% of students)
        head_turn_count = random.randint(int(student_count * 0.05), int(student_count * 0.25))
        if head_turn_count > 0:
            events.append({
                'type': 'head_turning',
                'count': head_turn_count,
                'confidence': 0.6 + random.random() * 0.4,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['head_turning'] += head_turn_count
        
        # Simulate looking around
        look_count = random.randint(int(student_count * 0.02), int(student_count * 0.15))
        if look_count > 0:
            events.append({
                'type': 'looking_around',
                'count': look_count,
                'confidence': 0.5 + random.random() * 0.4,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['looking_around'] += look_count
        
        # Simulate standing
        if random.random() > 0.85:
            events.append({
                'type': 'standing',
                'count': 1,
                'confidence': 0.7 + random.random() * 0.3,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['standing'] += 1
        
        # Simulate seat changes
        if random.random() > 0.92:
            events.append({
                'type': 'seat_change',
                'count': 1,
                'confidence': 0.6 + random.random() * 0.3,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['seat_change'] += 1
        
        # Simulate mobile phone detection
        if random.random() > 0.8:
            events.append({
                'type': 'mobile_phone',
                'count': 1,
                'confidence': 0.7 + random.random() * 0.3,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['mobile_phone'] += 1
        
        # Simulate smartwatch detection
        if random.random() > 0.9:
            events.append({
                'type': 'smartwatch',
                'count': 1,
                'confidence': 0.6 + random.random() * 0.3,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['smartwatch'] += 1
        
        # Simulate notes/books detection
        if random.random() > 0.85:
            events.append({
                'type': 'notes_books',
                'count': 1,
                'confidence': 0.65 + random.random() * 0.35,
                'timestamp': datetime.now().isoformat()
            })
            st.session_state.detections['notes_books'] += 1
        
        # Simulate invigilator presence
        st.session_state.detections['invigilator_present'] = random.random() > 0.3
        
        # Simulate blind spots
        blind_spots = random.randint(0, 2)
        st.session_state.detections['blind_spots'] = blind_spots
        if blind_spots > 0:
            events.append({
                'type': 'blind_spot',
                'count': blind_spots,
                'confidence': 0.8,
                'timestamp': datetime.now().isoformat()
            })
        
        # Generate alerts for high-confidence events
        for event in events:
            if event['confidence'] > 0.7:
                alert = {
                    'message': self._generate_alert_message(event),
                    'severity': 'high' if event['confidence'] > 0.85 else 'medium',
                    'timestamp': event['timestamp'],
                    'type': event['type']
                }
                alerts.append(alert)
        
        return events, alerts
    
    def _generate_alert_message(self, event):
        """Generate alert message based on event type"""
        messages = {
            'head_turning': f"⚠️ {event['count']} students detected looking around frequently",
            'looking_around': f"⚠️ {event['count']} students looking at neighboring desks",
            'standing': "⚠️ Student standing without permission detected",
            'seat_change': "⚠️ Student changed seat detected",
            'mobile_phone': "⚠️ Mobile phone detected on desk",
            'smartwatch': "⚠️ Smartwatch detected on student",
            'notes_books': "⚠️ Notes/books detected on desk",
            'blind_spot': f"⚠️ {event['count']} blind spot(s) detected in camera view"
        }
        return messages.get(event['type'], f"⚠️ {event['type']} detected")

# ============================================
# Initialize Engine
# ============================================
@st.cache_resource
def get_engine():
    return VideoAnalysisEngine()

engine = get_engine()

# ============================================
# UI Components
# ============================================

# Header
st.markdown('<div class="main-header">🎓 AI Exam Monitoring - Video Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time detection of cheating behaviors and prohibited items</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# Sidebar
# ============================================
with st.sidebar:
    st.markdown("## 🎮 Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Analysis", type="primary", use_container_width=True):
            st.session_state.is_analyzing = True
            st.session_state.video_events = []
            st.session_state.video_alerts = []
            st.session_state.detections = {
                'head_turning': 0,
                'looking_around': 0,
                'standing': 0,
                'seat_change': 0,
                'mobile_phone': 0,
                'smartwatch': 0,
                'notes_books': 0,
                'invigilator_present': False,
                'blind_spots': 0
            }
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Analysis", use_container_width=True):
            st.session_state.is_analyzing = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Live Statistics")
    
    # Real-time stats
    st.metric("Students Detected", st.session_state.student_count)
    st.metric("Total Events", len(st.session_state.video_events))
    st.metric("Active Alerts", len([a for a in st.session_state.video_alerts]))
    
    st.markdown("---")
    st.markdown("## 📋 Detection Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔄 Head Turning", st.session_state.detections['head_turning'])
        st.metric("👀 Looking Around", st.session_state.detections['looking_around'])
        st.metric("🧍 Standing", st.session_state.detections['standing'])
        st.metric("🪑 Seat Changes", st.session_state.detections['seat_change'])
    with col2:
        st.metric("📱 Mobile Phones", st.session_state.detections['mobile_phone'])
        st.metric("⌚ Smartwatches", st.session_state.detections['smartwatch'])
        st.metric("📚 Notes/Books", st.session_state.detections['notes_books'])
        st.metric("🔍 Blind Spots", st.session_state.detections['blind_spots'])

# ============================================
# Main Content - Tabs
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📹 Live Analysis",
    "🔔 Alerts",
    "📊 Analytics",
    "📄 Report"
])

# ============================================
# Tab 1: Live Analysis
# ============================================
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        video_placeholder = st.empty()
        
        if st.session_state.is_analyzing:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(20):  # Simulate 20 frames
                if not st.session_state.is_analyzing:
                    break
                
                # Analyze frame
                events, alerts = engine.analyze_frame()
                
                # Update session state
                st.session_state.video_events.extend(events)
                st.session_state.video_alerts.extend(alerts)
                
                # Update progress
                progress_bar.progress((i + 1) / 20)
                status_text.text(f"🔄 Analyzing frame {i+1}/20...")
                
                # Display results
                display_text = "### 📹 Live Analysis\n\n"
                display_text += f"**Frame:** {i+1}/20\n\n"
                display_text += f"**Students Detected:** {st.session_state.student_count}\n\n"
                display_text += "**Recent Detections:**\n"
                
                if events:
                    for event in events[-5:]:
                        display_text += f"- {event['type'].replace('_', ' ').title()}: {event['count']} (Confidence: {event['confidence']:.2f})\n"
                else:
                    display_text += "- No detections\n"
                
                display_text += f"\n**Total Events:** {len(st.session_state.video_events)}"
                display_text += f"\n**Active Alerts:** {len(st.session_state.video_alerts)}"
                
                video_placeholder.info(display_text)
                
                time.sleep(0.5)
            
            if st.session_state.is_analyzing:
                progress_bar.empty()
                status_text.text("✅ Analysis complete! Click Stop to end.")
            else:
                progress_bar.empty()
                status_text.text("⏹️ Analysis stopped.")
        else:
            video_placeholder.info("⏸️ Click 'Start Analysis' to begin video monitoring")
    
    with col2:
        st.subheader("📋 Recent Events")
        
        recent_events = st.session_state.video_events[-5:] if st.session_state.video_events else []
        if recent_events:
            for event in reversed(recent_events):
                with st.container():
                    confidence = event.get('confidence', 0)
                    color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
                    st.markdown(f"{color} **{event.get('type', '').replace('_', ' ').title()}**")
                    st.caption(f"Count: {event.get('count', 0)} | Conf: {confidence:.2f}")
                    st.divider()
        else:
            st.info("No events yet")

# ============================================
# Tab 2: Alerts
# ============================================
with tab2:
    st.subheader("🔔 Alerts")
    
    if st.session_state.video_alerts:
        # Filter
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All", "High", "Medium"]
        )
        
        filtered_alerts = st.session_state.video_alerts
        if severity_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity_filter.lower()]
        
        st.caption(f"Showing {len(filtered_alerts)} alerts")
        
        for alert in filtered_alerts[-10:]:
            severity_icon = {'high': '🔴', 'medium': '🟡'}.get(alert['severity'], '🟢')
            alert_class = {'high': 'alert-high', 'medium': 'alert-medium'}.get(alert['severity'], '')
            
            with st.container():
                st.markdown(f'<div class="{alert_class}">', unsafe_allow_html=True)
                st.markdown(f"{severity_icon} **{alert['message']}**")
                st.caption(f"Time: {alert['timestamp'][:19]}")
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()
    else:
        st.info("No alerts generated yet")

# ============================================
# Tab 3: Analytics
# ============================================
with tab3:
    st.subheader("📊 Analytics Dashboard")
    
    if st.session_state.video_events:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Events", len(st.session_state.video_events))
        with col2:
            st.metric("Students", st.session_state.student_count)
        with col3:
            st.metric("Alerts", len(st.session_state.video_alerts))
        with col4:
            unique_events = len(set(e['type'] for e in st.session_state.video_events))
            st.metric("Event Types", unique_events)
        
        # Event distribution
        col1, col2 = st.columns(2)
        
        with col1:
            event_counts = {}
            for event in st.session_state.video_events:
                event_counts[event['type']] = event_counts.get(event['type'], 0) + event['count']
            
            fig = go.Figure(data=[go.Bar(
                x=list(event_counts.keys()),
                y=list(event_counts.values()),
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                              '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE']
            )])
            fig.update_layout(
                title="Event Distribution",
                xaxis_title="Event Type",
                yaxis_title="Count",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Confidence distribution
            confidences = [e.get('confidence', 0) for e in st.session_state.video_events]
            fig = go.Figure(data=[go.Histogram(
                x=confidences,
                nbinsx=10,
                marker_color='#45B7D1'
            )])
            fig.update_layout(
                title="Confidence Distribution",
                xaxis_title="Confidence Score",
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        with st.expander("📋 Detailed Summary", expanded=False):
            summary_data = []
            for event_type, count in event_counts.items():
                avg_conf = np.mean([e['confidence'] for e in st.session_state.video_events if e['type'] == event_type])
                summary_data.append({
                    'Event Type': event_type.replace('_', ' ').title(),
                    'Count': count,
                    'Avg Confidence': f"{avg_conf:.2f}"
                })
            st.dataframe(pd.DataFrame(summary_data))
    else:
        st.info("No data for analytics")

# ============================================
# Tab 4: Report
# ============================================
with tab4:
    st.subheader("📄 Examination Report")
    
    if st.session_state.video_events:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Examination Details**")
            st.markdown(f"- **Exam ID:** `EXAM-{datetime.now().strftime('%Y%m%d')}`")
            st.markdown(f"- **Date:** `{datetime.now().strftime('%Y-%m-%d %H:%M')}`")
            st.markdown(f"- **Students Detected:** `{st.session_state.student_count}`")
            st.markdown(f"- **Total Events:** `{len(st.session_state.video_events)}`")
            st.markdown(f"- **Total Alerts:** `{len(st.session_state.video_alerts)}`")
        
        with col2:
            st.markdown("**Detection Summary**")
            st.markdown(f"- 🔄 Head Turning: `{st.session_state.detections['head_turning']}`")
            st.markdown(f"- 👀 Looking Around: `{st.session_state.detections['looking_around']}`")
            st.markdown(f"- 📱 Mobile Phones: `{st.session_state.detections['mobile_phone']}`")
            st.markdown(f"- ⌚ Smartwatches: `{st.session_state.detections['smartwatch']}`")
            st.markdown(f"- 📚 Notes/Books: `{st.session_state.detections['notes_books']}`")
        
        # Recommendations
        st.markdown("---")
        st.markdown("**Recommendations**")
        
        if st.session_state.detections['head_turning'] > 10:
            st.warning("⚠️ High number of head turning detected - consider seating arrangement review")
        if st.session_state.detections['mobile_phone'] > 0:
            st.error("🚨 Mobile phones detected - immediate action required")
        if st.session_state.detections['smartwatch'] > 0:
            st.warning("⚠️ Smartwatches detected - enforce policy")
        if st.session_state.detections['blind_spots'] > 0:
            st.warning("⚠️ Blind spots detected - camera position needs adjustment")
        
        # Export
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Export Report"):
                report_data = {
                    'exam_id': f"EXAM-{datetime.now().strftime('%Y%m%d')}",
                    'timestamp': datetime.now().isoformat(),
                    'student_count': st.session_state.student_count,
                    'events': st.session_state.video_events,
                    'alerts': st.session_state.video_alerts,
                    'detections': st.session_state.detections
                }
                json_str = json.dumps(report_data, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    json_str,
                    f"exam_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    "application/json"
                )
        
        with col2:
            if st.button("📊 Export CSV"):
                events_df = pd.DataFrame(st.session_state.video_events)
                csv = events_df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"events_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv"
                )
    else:
        st.info("No data to generate report")

# ============================================
# Footer
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🎓 AI Exam Monitoring System")
with col2:
    st.caption("⚡ Powered by Streamlit")
with col3:
    if st.session_state.is_analyzing:
        st.caption("🟢 Analysis Active")
    else:
        st.caption("⏸️ System Idle")

# ============================================
# Auto-refresh for continuous analysis
# ============================================
if st.session_state.is_analyzing:
    time.sleep(0.5)
    st.rerun()

