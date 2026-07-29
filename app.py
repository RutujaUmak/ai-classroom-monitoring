# ============================================
# app.py - Complete AI Classroom Monitoring System
# All Requirements: RAG, AI Agents, Dashboard, Reporting
# ============================================

import streamlit as st
import time
import random
import json
import os
import base64
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="AI Classroom Monitoring System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        transition: transform 0.2s;
        text-align: center;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #888;
        margin-top: 5px;
    }
    
    /* Alerts */
    .alert-high {
        background: #ffebee;
        border-left: 5px solid #f44336;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 6px;
    }
    .alert-medium {
        background: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 6px;
    }
    .alert-low {
        background: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 6px;
    }
    
    /* Status */
    .status-active {
        color: #4caf50;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .status-idle {
        color: #ff9800;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Evidence Box */
    .evidence-box {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 15px;
        margin: 8px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    /* Policy Cards */
    .policy-card {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .policy-title {
        font-weight: 600;
        color: #1f77b4;
    }
    .policy-category {
        display: inline-block;
        background: #e3f2fd;
        color: #1565c0;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    
    /* Report */
    .report-section {
        background: #fafafa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e8e8e8;
    }
    
    /* Sidebar */
    .sidebar-section {
        padding: 5px 0;
    }
    
    /* Animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .pulsing {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; }
        .metric-value { font-size: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.is_processing = False
    st.session_state.exam_id = f"EXAM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    st.session_state.exam_start_time = datetime.now()
    
    # Data Stores
    st.session_state.events = []
    st.session_state.alerts = []
    st.session_state.evidence = []
    st.session_state.reports = []
    st.session_state.students = {}
    
    # Statistics
    st.session_state.total_frames = 0
    st.session_state.prohibited_count = 0
    st.session_state.behavior_count = 0
    st.session_state.confirmed_violations = 0
    st.session_state.dismissed_alerts = 0
    st.session_state.camera_status = "Active"
    st.session_state.camera_uptime = 0
    
    # Student Tracking (simulated)
    st.session_state.student_count = 0
    st.session_state.student_positions = {}
    
    # Settings
    st.session_state.confidence_threshold = 0.5
    st.session_state.detection_speed = 5
    st.session_state.policy_query = ""

# ============================================
# RAG SYSTEM - Complete Knowledge Base
# ============================================
class RAGSystem:
    def __init__(self):
        self.policies = [
            # Prohibited Items
            {
                'id': 'POL-001',
                'title': 'Mobile Phone Policy',
                'content': 'Mobile phones are strictly prohibited during examinations. If a student is found with a mobile phone, it will be confiscated and the student may face disciplinary action including potential expulsion.',
                'category': 'Prohibited Items',
                'keywords': ['phone', 'mobile', 'cell', 'smartphone', 'iphone', 'android', 'device'],
                'actions': ['Confiscate device', 'Document incident', 'Report to coordinator', 'Student interview']
            },
            {
                'id': 'POL-002',
                'title': 'Smartwatch Policy',
                'content': 'Smartwatches and wearable devices are not permitted in examination halls. Students must remove and store them before entering the examination venue.',
                'category': 'Prohibited Items',
                'keywords': ['watch', 'smartwatch', 'wearable', 'apple watch', 'fitness tracker', 'fitbit'],
                'actions': ['Ask student to remove device', 'Store in designated area', 'Document violation']
            },
            {
                'id': 'POL-003',
                'title': 'Books and Notes Policy',
                'content': 'Books, notes, and any unauthorized materials are strictly prohibited in the examination hall. All such items must be placed in designated areas before the exam begins.',
                'category': 'Prohibited Items',
                'keywords': ['book', 'note', 'textbook', 'paper', 'cheat sheet', 'material', 'unauthorized'],
                'actions': ['Confiscate materials', 'Document incident', 'Report to coordinator']
            },
            {
                'id': 'POL-004',
                'title': 'Electronic Devices Policy',
                'content': 'All electronic devices including laptops, tablets, earbuds, and calculators (unless specified) are prohibited during examinations.',
                'category': 'Prohibited Items',
                'keywords': ['laptop', 'tablet', 'earbuds', 'calculator', 'electronic', 'device', 'gadget'],
                'actions': ['Confiscate device', 'Document incident', 'Report to coordinator']
            },
            
            # Behavior Policies
            {
                'id': 'POL-005',
                'title': 'Suspicious Behavior Protocol',
                'content': 'If a student is observed displaying suspicious behavior such as frequent head turning, looking at neighboring desks, using unauthorized materials, or any unusual movements, the invigilator should document the incident and report to the examination coordinator immediately.',
                'category': 'Behavior',
                'keywords': ['behavior', 'suspicious', 'turning', 'looking', 'cheating', 'unusual', 'movement'],
                'actions': ['Observe and document', 'Warn student if appropriate', 'Report to coordinator', 'File incident report']
            },
            {
                'id': 'POL-006',
                'title': 'Group Interaction Policy',
                'content': 'Students are not permitted to communicate or interact with other students during examinations. Any form of communication, including talking, passing notes, or gesturing, is considered a violation.',
                'category': 'Behavior',
                'keywords': ['group', 'interaction', 'communication', 'talking', 'passing notes', 'gesturing'],
                'actions': ['Separate students if possible', 'Document incident', 'Report to coordinator']
            },
            {
                'id': 'POL-007',
                'title': 'Student Movement Policy',
                'content': 'Students should remain in their designated seats during the examination. Unauthorized standing, moving, or changing seats is not permitted without invigilator approval.',
                'category': 'Behavior',
                'keywords': ['movement', 'standing', 'walking', 'seat change', 'leaving', 'unauthorized'],
                'actions': ['Redirect student to seat', 'Document incident', 'Report if repeated']
            },
            
            # Procedures
            {
                'id': 'POL-008',
                'title': 'Evidence Collection Procedure',
                'content': 'All suspected violations must be documented with timestamp, camera footage, and student identification. Evidence should be preserved for review by the examination committee.',
                'category': 'Procedure',
                'keywords': ['evidence', 'documentation', 'footage', 'timestamp', 'proof', 'record', 'preserve'],
                'actions': ['Capture timestamp', 'Save camera footage', 'Record student ID', 'Preserve evidence']
            },
            {
                'id': 'POL-009',
                'title': 'Incident Reporting Procedure',
                'content': 'Incident reports should include: student ID, exam details, nature of violation, evidence collected, timestamp, and recommended action. Reports should be submitted within 24 hours of the examination.',
                'category': 'Procedure',
                'keywords': ['report', 'incident', 'submit', 'document', 'reporting', 'form', 'procedure'],
                'actions': ['Fill incident report', 'Attach evidence', 'Submit to coordinator', 'Follow up']
            },
            {
                'id': 'POL-010',
                'title': 'Invigilator Duties',
                'content': 'Invigilators must monitor examination halls, maintain order, report violations, and ensure all rules are followed. They should remain vigilant throughout the exam and document any suspicious activities.',
                'category': 'Staff',
                'keywords': ['invigilator', 'monitor', 'supervise', 'duty', 'responsibility', 'vigilant', 'staff'],
                'actions': ['Maintain vigilance', 'Document activities', 'Report violations', 'Ensure compliance']
            },
            {
                'id': 'POL-011',
                'title': 'Academic Integrity Policy',
                'content': 'Academic integrity is the foundation of our institution. Any form of academic dishonesty, including cheating, plagiarism, or unauthorized collaboration, is strictly prohibited and will result in disciplinary action.',
                'category': 'Academic Integrity',
                'keywords': ['integrity', 'honesty', 'cheating', 'plagiarism', 'dishonesty', 'ethics'],
                'actions': ['Document violation', 'Report to committee', 'Follow disciplinary procedure']
            },
            
            # Emergency Procedures
            {
                'id': 'POL-012',
                'title': 'Emergency Protocol',
                'content': 'In case of emergency, invigilators should follow the institution\'s emergency procedures. This includes evacuating students, contacting emergency services, and documenting the situation.',
                'category': 'Emergency',
                'keywords': ['emergency', 'fire', 'medical', 'evacuation', 'safety', 'crisis'],
                'actions': ['Follow emergency procedures', 'Evacuate if necessary', 'Contact emergency services', 'Document incident']
            },
            
            # Examination Rules
            {
                'id': 'POL-013',
                'title': 'Examination Rules',
                'content': 'Students must follow all examination rules including: no communication with other students, no unauthorized materials, no electronic devices, and remaining in designated seats.',
                'category': 'Rules',
                'keywords': ['rules', 'examination', 'guidelines', 'instructions', 'procedures'],
                'actions': ['Review rules with students', 'Enforce compliance', 'Document violations']
            },
            {
                'id': 'POL-014',
                'title': 'Student Identification',
                'content': 'Students must present valid identification before the examination begins. Invigilators should verify student identities and maintain an attendance record.',
                'category': 'Rules',
                'keywords': ['identification', 'id', 'verify', 'identity', 'student', 'attendance'],
                'actions': ['Verify ID', 'Mark attendance', 'Document discrepancies']
            }
        ]
        
        # Initialize vector store (simulated)
        self.vector_store = {}
        for policy in self.policies:
            self.vector_store[policy['id']] = {
                'content': policy['content'],
                'keywords': policy['keywords'],
                'category': policy['category']
            }
    
    def semantic_search(self, query, top_k=5):
        """Perform semantic search on policies"""
        query_lower = query.lower()
        results = []
        
        for policy in self.policies:
            # Calculate relevance score
            score = 0.0
            
            # Check keywords
            for keyword in policy['keywords']:
                if keyword.lower() in query_lower:
                    score += 0.2
            
            # Check title
            if any(word.lower() in query_lower for word in policy['title'].split()):
                score += 0.3
            
            # Check category
            if policy['category'].lower() in query_lower:
                score += 0.15
            
            # Check content
            if any(word.lower() in policy['content'].lower() for word in query_lower.split() if len(word) > 3):
                score += 0.1
            
            if score > 0:
                results.append({
                    'document': policy,
                    'score': min(score, 1.0)
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
    
    def get_policy_by_id(self, policy_id):
        """Get policy by ID"""
        for policy in self.policies:
            if policy['id'] == policy_id:
                return policy
        return None
    
    def get_policies_by_category(self, category):
        """Get all policies in a category"""
        return [p for p in self.policies if p['category'] == category]

# ============================================
# AI AGENT SYSTEM
# ============================================

class AlertAgent:
    def __init__(self):
        self.alert_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        self.alert_history = []
    
    def process_event(self, event):
        """Process event and generate alert if threshold exceeded"""
        confidence = event.get('confidence', 0.0)
        
        if confidence >= self.alert_thresholds['high']:
            severity = 'high'
        elif confidence >= self.alert_thresholds['medium']:
            severity = 'medium'
        elif confidence >= self.alert_thresholds['low']:
            severity = 'low'
        else:
            return None
        
        alert = {
            'alert_id': f"ALT-{len(self.alert_history)+1}",
            'event_id': event.get('event_id', f"EVT-{len(self.alert_history)+1}"),
            'severity': severity,
            'message': self._generate_message(event, severity),
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'status': 'active',
            'actions': event.get('actions', ['Review and take appropriate action']),
            'policy_reference': event.get('policy_reference', None)
        }
        
        self.alert_history.append(alert)
        return alert
    
    def _generate_message(self, event, severity):
        """Generate alert message"""
        sub_type = event.get('sub_type', 'unknown').replace('_', ' ').title()
        if severity == 'high':
            return f"⚠️ HIGH: {sub_type} detected - Immediate action required"
        elif severity == 'medium':
            return f"⚡ MEDIUM: {sub_type} detected - Review recommended"
        else:
            return f"ℹ️ LOW: {sub_type} detected - Monitor situation"

class EvidenceAgent:
    def __init__(self):
        self.evidence_store = []
    
    def capture_evidence(self, event, frame_data=None):
        """Capture evidence for an event"""
        evidence = {
            'evidence_id': f"EVID-{len(self.evidence_store)+1}",
            'event_id': event.get('event_id', f"EVT-{len(self.evidence_store)+1}"),
            'event_type': event.get('type', 'unknown'),
            'sub_type': event.get('sub_type', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'confidence': event.get('confidence', 0.0),
            'snapshot': {
                'description': f"Snapshot of {event.get('sub_type', 'event')}",
                'bbox': event.get('bbox', [100, 100, 200, 200]),
                'confidence': event.get('confidence', 0.0)
            },
            'metadata': {
                'exam_id': st.session_state.exam_id,
                'camera_id': 'CAM-001',
                'location': 'Examination Hall A',
                'frame_number': st.session_state.total_frames
            },
            'policy_reference': event.get('policy_reference', None)
        }
        self.evidence_store.append(evidence)
        st.session_state.evidence.append(evidence)
        return evidence
    
    def get_evidence_by_event(self, event_id):
        """Get evidence for a specific event"""
        return [e for e in self.evidence_store if e['event_id'] == event_id]
    
    def get_latest_evidence(self, limit=5):
        """Get latest evidence"""
        return self.evidence_store[-limit:] if self.evidence_store else []

class ReportAgent:
    def __init__(self):
        self.reports = []
    
    def generate_report(self, exam_id, events, alerts, evidence):
        """Generate comprehensive report"""
        report = {
            'report_id': f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'exam_id': exam_id,
            'generated_at': datetime.now().isoformat(),
            'duration': {
                'start': st.session_state.exam_start_time.isoformat(),
                'end': datetime.now().isoformat(),
                'total_minutes': (datetime.now() - st.session_state.exam_start_time).total_seconds() / 60
            },
            'summary': self._generate_summary(events, alerts),
            'statistics': self._generate_statistics(events, alerts),
            'events': events[-20:] if len(events) > 20 else events,
            'alerts': alerts[-10:] if len(alerts) > 10 else alerts,
            'evidence': evidence[-5:] if len(evidence) > 5 else evidence,
            'total_events': len(events),
            'total_alerts': len(alerts),
            'confirmed_violations': st.session_state.confirmed_violations,
            'dismissed_alerts': st.session_state.dismissed_alerts,
            'recommendations': self._generate_recommendations(events, alerts),
            'camera_status': st.session_state.camera_status,
            'total_frames': st.session_state.total_frames
        }
        self.reports.append(report)
        st.session_state.reports.append(report)
        return report
    
    def _generate_summary(self, events, alerts):
        """Generate executive summary"""
        prohibited = len([e for e in events if e.get('type') == 'prohibited_object'])
        behavior = len([e for e in events if e.get('type') == 'suspicious_behavior'])
        group = len([e for e in events if e.get('type') == 'group_interaction'])
        
        high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
        medium_alerts = len([a for a in alerts if a.get('severity') == 'medium'])
        
        return {
            'total_events': len(events),
            'prohibited_items': prohibited,
            'suspicious_behaviors': behavior,
            'group_interactions': group,
            'high_alerts': high_alerts,
            'medium_alerts': medium_alerts,
            'overall_status': 'Normal' if len(alerts) < 5 else 'Caution' if len(alerts) < 15 else 'High Alert',
            'summary_text': f"""
                Examination monitoring completed.
                • {len(events)} total events detected
                • {prohibited} prohibited items found
                • {behavior} suspicious behaviors observed
                • {group} group interactions detected
                • {len(alerts)} alerts generated ({high_alerts} high priority)
                • {st.session_state.confirmed_violations} violations confirmed
            """
        }
    
    def _generate_statistics(self, events, alerts):
        """Generate detailed statistics"""
        return {
            'total_events': len(events),
            'events_per_minute': len(events) / max(1, (datetime.now() - st.session_state.exam_start_time).total_seconds() / 60),
            'prohibited_items': len([e for e in events if e.get('type') == 'prohibited_object']),
            'suspicious_behaviors': len([e for e in events if e.get('type') == 'suspicious_behavior']),
            'group_interactions': len([e for e in events if e.get('type') == 'group_interaction']),
            'alerts_generated': len(alerts),
            'high_alerts': len([a for a in alerts if a.get('severity') == 'high']),
            'medium_alerts': len([a for a in alerts if a.get('severity') == 'medium']),
            'low_alerts': len([a for a in alerts if a.get('severity') == 'low']),
            'confirmed_violations': st.session_state.confirmed_violations,
            'dismissed_alerts': st.session_state.dismissed_alerts,
            'avg_confidence': sum(e.get('confidence', 0) for e in events) / max(1, len(events)),
            'unique_events': len(set(e.get('sub_type', '') for e in events)),
            'total_frames': st.session_state.total_frames,
            'camera_uptime': (datetime.now() - st.session_state.exam_start_time).total_seconds() / 60
        }
    
    def _generate_recommendations(self, events, alerts):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for high number of prohibited items
        prohibited = [e for e in events if e.get('type') == 'prohibited_object']
        if len(prohibited) > 3:
            recommendations.append("🔴 High number of prohibited items detected. Review security protocols.")
        
        # Check for suspicious behavior patterns
        behavior = [e for e in events if e.get('type') == 'suspicious_behavior']
        if len(behavior) > 5:
            recommendations.append("🟡 Multiple suspicious behaviors detected. Consider additional invigilators.")
        
        # Check for group interactions
        group = [e for e in events if e.get('type') == 'group_interaction']
        if len(group) > 2:
            recommendations.append("🟡 Group interactions detected. Review seating arrangement.")
        
        # Check alert rate
        if len(alerts) > 10:
            recommendations.append("🟡 High alert rate. Review detection thresholds.")
        
        # Check camera status
        if st.session_state.camera_status != "Active":
            recommendations.append("🔴 Camera status issue. Check camera connection.")
        
        if not recommendations:
            recommendations.append("✅ All monitoring parameters within normal range.")
        
        return recommendations
    
    def export_report_json(self, report):
        """Export report as JSON"""
        return json.dumps(report, indent=2)
    
    def export_report_csv(self, report):
        """Export report data as CSV"""
        events_df = pd.DataFrame(report['events'])
        return events_df.to_csv(index=False)

# ============================================
# DATA GENERATION ENGINE (Realistic Simulation)
# ============================================

class DataGenerationEngine:
    def __init__(self):
        self.prohibited_items = [
            'cell phone', 'smartwatch', 'book', 'calculator', 
            'earbuds', 'laptop', 'notes', 'tablet'
        ]
        self.behaviors = [
            'head_turning', 'body_leaning', 'looking_around', 
            'suspicious_hand_movement', 'standing_up', 'seat_changing'
        ]
        self.event_probabilities = {
            'prohibited_object': 0.3,
            'suspicious_behavior': 0.25,
            'group_interaction': 0.1
        }
        self.student_ids = [f"S{str(i).zfill(3)}" for i in range(1, 31)]
        self.student_positions = {}
        
    def generate_event(self):
        """Generate a single event with realistic data"""
        event_type = random.choices(
            list(self.event_probabilities.keys()),
            weights=list(self.event_probabilities.values())
        )[0]
        
        confidence = 0.6 + random.random() * 0.4
        timestamp = datetime.now().isoformat()
        student_id = random.choice(self.student_ids)
        
        event = {
            'event_id': f"EVT-{random.randint(1000, 9999)}",
            'type': event_type,
            'sub_type': random.choice(self.prohibited_items if event_type == 'prohibited_object' else self.behaviors),
            'confidence': confidence,
            'timestamp': timestamp,
            'student_id': student_id,
            'status': 'pending',
            'icon': self._get_icon(event_type),
            'bbox': self._generate_bbox(),
            'severity': self._calculate_severity(confidence)
        }
        
        return event
    
    def _get_icon(self, event_type):
        """Get icon for event type"""
        icons = {
            'prohibited_object': '⚠️',
            'suspicious_behavior': '👤',
            'group_interaction': '👥'
        }
        return icons.get(event_type, '📌')
    
    def _generate_bbox(self):
        """Generate random bounding box"""
        x = random.randint(100, 500)
        y = random.randint(100, 300)
        w = random.randint(50, 150)
        h = random.randint(50, 150)
        return [x, y, x + w, y + h]
    
    def _calculate_severity(self, confidence):
        """Calculate severity based on confidence"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def generate_batch(self, count=5):
        """Generate a batch of events"""
        return [self.generate_event() for _ in range(count)]

# ============================================
# INITIALIZE SYSTEM COMPONENTS
# ============================================

@st.cache_resource
def initialize_system():
    rag = RAGSystem()
    alert_agent = AlertAgent()
    evidence_agent = EvidenceAgent()
    report_agent = ReportAgent()
    data_engine = DataGenerationEngine()
    return rag, alert_agent, evidence_agent, report_agent, data_engine

rag, alert_agent, evidence_agent, report_agent, data_engine = initialize_system()

# ============================================
# CORE PROCESSING FUNCTION
# ============================================

def process_frame():
    """Process a single frame with complete pipeline"""
    if not st.session_state.is_processing:
        return None
    
    st.session_state.total_frames += 1
    st.session_state.camera_uptime += 0.5
    
    # Generate events
    events = data_engine.generate_batch(random.randint(1, 3))
    
    processed_events = []
    processed_alerts = []
    
    for event in events:
        # Get policy reference
        policy_results = rag.semantic_search(event['sub_type'], top_k=1)
        if policy_results:
            event['policy_reference'] = policy_results[0]['document']['id']
            event['policy_content'] = policy_results[0]['document']['content']
            event['actions'] = policy_results[0]['document'].get('actions', [])
        
        # Process with Alert Agent
        alert = alert_agent.process_event(event)
        if alert:
            processed_alerts.append(alert)
            st.session_state.alerts.append(alert)
        
        # Capture evidence
        evidence = evidence_agent.capture_evidence(event)
        if evidence:
            st.session_state.evidence.append(evidence)
        
        # Update counts
        if event['type'] == 'prohibited_object':
            st.session_state.prohibited_count += 1
        elif event['type'] == 'suspicious_behavior':
            st.session_state.behavior_count += 1
        
        processed_events.append(event)
    
    st.session_state.events.extend(processed_events)
    
    return {
        'events': processed_events,
        'alerts': processed_alerts,
        'evidence': st.session_state.evidence[-5:] if st.session_state.evidence else []
    }

# ============================================
# COMPLETE STREAMLIT UI
# ============================================

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="font-size: 1.8rem; color: #1f77b4; margin: 0;">🎓 AI Monitor</h1>
        <p style="color: #888; font-size: 0.8rem; margin: 0;">Classroom Monitoring System</p>
        <hr>
    </div>
    """, unsafe_allow_html=True)
    
    # Exam Info
    st.markdown(f"**📋 Exam ID:** `{st.session_state.exam_id}`")
    st.markdown(f"**🕐 Started:** `{st.session_state.exam_start_time.strftime('%H:%M:%S')}`")
    st.markdown("---")
    
    # Controls
    st.subheader("🎮 Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", type="primary", use_container_width=True):
            st.session_state.is_processing = True
            st.session_state.exam_start_time = datetime.now()
            st.rerun()
    with col2:
        if st.button("⏹️ Stop", type="secondary", use_container_width=True):
            st.session_state.is_processing = False
            # Generate report on stop
            if st.session_state.events:
                report_agent.generate_report(
                    st.session_state.exam_id,
                    st.session_state.events,
                    st.session_state.alerts,
                    st.session_state.evidence
                )
            st.rerun()
    
    # Quick Actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    if st.button("📊 Generate Report", use_container_width=True):
        if st.session_state.events:
            report = report_agent.generate_report(
                st.session_state.exam_id,
                st.session_state.events,
                st.session_state.alerts,
                st.session_state.evidence
            )
            st.success(f"✅ Report generated: {report['report_id']}")
        else:
            st.warning("No events to report")
    
    if st.button("🗑️ Clear Data", use_container_width=True):
        st.session_state.events = []
        st.session_state.alerts = []
        st.session_state.evidence = []
        st.session_state.reports = []
        st.session_state.prohibited_count = 0
        st.session_state.behavior_count = 0
        st.rerun()
    
    # Settings
    st.markdown("---")
    with st.expander("⚙️ Settings", expanded=False):
        confidence_threshold = st.slider(
            "Confidence Threshold",
            0.1, 1.0, 0.5, 0.05,
            help="Higher threshold = fewer but more accurate detections"
        )
        st.session_state.confidence_threshold = confidence_threshold
        
        detection_speed = st.slider(
            "Detection Speed",
            1, 10, 5,
            help="Higher = faster frame processing"
        )
        st.session_state.detection_speed = detection_speed
        
        camera_id = st.selectbox(
            "Camera ID",
            ["CAM-001", "CAM-002", "CAM-003"],
            index=0
        )
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Live Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Events", len(st.session_state.events))
        st.metric("Alerts", len(st.session_state.alerts))
    with col2:
        st.metric("Prohibited", st.session_state.prohibited_count)
        st.metric("Suspicious", st.session_state.behavior_count)
    
    # Status
    st.markdown("---")
    status = "🟢 Active" if st.session_state.is_processing else "⏸️ Idle"
    status_class = "status-active" if st.session_state.is_processing else "status-idle"
    st.markdown(f'<div class="{status_class}">Status: {status}</div>', unsafe_allow_html=True)
    st.caption(f"Frames: {st.session_state.total_frames}")

# ============================================
# MAIN CONTENT
# ============================================
st.markdown('<div class="main-header">🎓 AI-Powered Classroom Monitoring</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time AI Monitoring with RAG & Multi-Agent System</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📹 Live Feed",
    "🔔 Alerts",
    "📈 Analytics",
    "📚 Policy Assistant",
    "📄 Reports & Evidence",
    "🤖 AI Agents"
])

# ============================================
# TAB 1: LIVE FEED
# ============================================
with tab1:
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        video_placeholder = st.empty()
        
        if st.session_state.is_processing:
            # Simulate live feed
            feed_container = st.container()
            
            with feed_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process 30 frames for demo
                for i in range(30):
                    if not st.session_state.is_processing:
                        break
                    
                    result = process_frame()
                    progress_bar.progress((i + 1) / 30)
                    status_text.text(f"🔄 Processing frame {i+1}/30...")
                    
                    # Display detection info
                    detection_info = ""
                    if result and result['events']:
                        for event in result['events']:
                            icon = event.get('icon', '•')
                            detection_info += f"{icon} {event['sub_type'].replace('_', ' ').title()} ({event['confidence']:.2f})\n"
                    else:
                        detection_info = "No detections"
                    
                    video_placeholder.info(
                        f"📹 **Live Feed**\n\n"
                        f"**Detections:**\n{detection_info}\n\n"
                        f"**Total Events:** {len(st.session_state.events)}\n"
                        f"**Active Alerts:** {len(st.session_state.alerts)}\n"
                        f"**Evidence:** {len(st.session_state.evidence)}"
                    )
                    
                    time.sleep(0.5 / st.session_state.detection_speed)
                
                if st.session_state.is_processing:
                    progress_bar.empty()
                    status_text.text("✅ Monitoring active! Click Stop to end.")
                else:
                    progress_bar.empty()
                    status_text.text("⏹️ Monitoring stopped.")
        else:
            video_placeholder.info("⏸️ Click 'Start' to begin monitoring")
    
    with col2:
        st.subheader("📋 Recent Events")
        if st.session_state.events:
            for event in st.session_state.events[-5:]:
                confidence = event.get('confidence', 0)
                icon = event.get('icon', '•')
                color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.5 else "🔴"
                st.markdown(f"{color} {icon} **{event.get('sub_type', '').replace('_', ' ').title()}**")
                st.caption(f"ID: {event.get('student_id', 'N/A')} | Conf: {confidence:.2f}")
                st.divider()
        else:
            st.info("No events")
    
    with col3:
        st.subheader("📊 Quick Stats")
        st.metric("Total Frames", st.session_state.total_frames)
        st.metric("Camera Uptime", f"{st.session_state.camera_uptime:.1f}min")
        st.metric("Students Detected", len(set(e.get('student_id', '') for e in st.session_state.events)))

# ============================================
# TAB 2: ALERTS
# ============================================
with tab2:
    st.subheader("🔔 Alerts & Events")
    
    if st.session_state.alerts:
        alerts_df = pd.DataFrame(st.session_state.alerts)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity",
                ["All", "High", "Medium", "Low"]
            )
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Active", "Resolved", "Dismissed"]
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Time (Newest)", "Time (Oldest)", "Confidence (High)", "Confidence (Low)"]
            )
        
        # Apply filters
        filtered_df = alerts_df.copy()
        if severity_filter != "All":
            filtered_df = filtered_df[filtered_df['severity'] == severity_filter.lower()]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter.lower()]
        
        # Apply sorting
        if sort_by == "Time (Newest)":
            filtered_df = filtered_df.sort_values('timestamp', ascending=False)
        elif sort_by == "Time (Oldest)":
            filtered_df = filtered_df.sort_values('timestamp', ascending=True)
        elif sort_by == "Confidence (High)":
            filtered_df = filtered_df.sort_values('confidence', ascending=False)
        elif sort_by == "Confidence (Low)":
            filtered_df = filtered_df.sort_values('confidence', ascending=True)
        
        st.caption(f"Showing {len(filtered_df)} alerts")
        
        for _, alert in filtered_df.iterrows():
            severity_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(alert['severity'], '⚪')
            
            alert_class = {
                'high': 'alert-high',
                'medium': 'alert-medium',
                'low': 'alert-low'
            }.get(alert['severity'], '')
            
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.markdown(f'<div class="{alert_class}">', unsafe_allow_html=True)
                    st.markdown(f"{severity_icon} **{alert['message']}**")
                    if 'policy_reference' in alert:
                        policy = rag.get_policy_by_id(alert['policy_reference'])
                        if policy:
                            st.caption(f"📚 Policy: {policy['title']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.text(f"Confidence: {alert['confidence']:.2f}")
                    st.text(f"Status: {alert['status']}")
                with col3:
                    if alert.get('status') == 'active':
                        if st.button("✅ Resolve", key=f"resolve_{alert.get('timestamp', '')}"):
                            alert['status'] = 'resolved'
                            st.session_state.confirmed_violations += 1
                            st.rerun()
                        if st.button("❌ Dismiss", key=f"dismiss_{alert.get('timestamp', '')}"):
                            alert['status'] = 'dismissed'
                            st.session_state.dismissed_alerts += 1
                            st.rerun()
                st.divider()
    else:
        st.info("No alerts generated yet")

# ============================================
# TAB 3: ANALYTICS
# ============================================
with tab3:
    st.subheader("📈 Analytics Dashboard")
    
    if st.session_state.events:
        events_df = pd.DataFrame(st.session_state.events)
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Events", len(st.session_state.events))
        with col2:
            unique_types = len(events_df['sub_type'].unique()) if 'sub_type' in events_df else 0
            st.metric("Event Types", unique_types)
        with col3:
            high_conf = sum(1 for e in st.session_state.events if e.get('confidence', 0) > 0.7)
            st.metric("High Confidence", high_conf)
        with col4:
            alert_rate = len(st.session_state.alerts) / max(1, len(st.session_state.events))
            st.metric("Alert Rate", f"{alert_rate:.2f}")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sub_type' in events_df:
                event_counts = events_df['sub_type'].value_counts().head(10)
                fig = go.Figure(data=[go.Bar(
                    x=event_counts.index,
                    y=event_counts.values,
                    marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                                  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'],
                    text=event_counts.values,
                    textposition='auto'
                )])
                fig.update_layout(
                    title="Top Event Types",
                    xaxis_title="Event Type",
                    yaxis_title="Count",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'severity' in pd.DataFrame(st.session_state.alerts).columns:
                severity_counts = pd.DataFrame(st.session_state.alerts)['severity'].value_counts()
                fig = go.Figure(data=[go.Pie(
                    labels=severity_counts.index,
                    values=severity_counts.values,
                    marker=dict(colors=['#f44336', '#ff9800', '#4caf50']),
                    hole=0.4
                )])
                fig.update_layout(
                    title="Alert Severity Distribution",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            # Confidence Distribution
            confidences = [e.get('confidence', 0) for e in st.session_state.events]
            fig = go.Figure(data=[go.Histogram(
                x=confidences,
                nbinsx=10,
                marker_color='#45B7D1',
                name='Events'
            )])
            fig.update_layout(
                title="Confidence Distribution",
                xaxis_title="Confidence Score",
                yaxis_title="Frequency",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Events Timeline
            if len(st.session_state.events) > 1:
                timeline_df = pd.DataFrame(st.session_state.events)
                timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
                timeline_df = timeline_df.sort_values('timestamp')
                
                # Group by minute
                timeline_df['minute'] = timeline_df['timestamp'].dt.floor('min')
                minute_counts = timeline_df.groupby('minute').size().reset_index(name='count')
                
                fig = go.Figure(data=[go.Scatter(
                    x=minute_counts['minute'],
                    y=minute_counts['count'],
                    mode='lines+markers',
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=8, color='#1f77b4'),
                    fill='tozeroy',
                    fillcolor='rgba(31, 119, 180, 0.2)'
                )])
                fig.update_layout(
                    title="Events Timeline (per minute)",
                    xaxis_title="Time",
                    yaxis_title="Events per Minute",
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional Stats
        with st.expander("📊 Detailed Statistics", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Event Statistics")
                st.dataframe(events_df.describe())
            with col2:
                if st.session_state.alerts:
                    alerts_df = pd.DataFrame(st.session_state.alerts)
                    st.subheader("Alert Statistics")
                    st.dataframe(alerts_df.describe())
    
    else:
        st.info("No data for analytics. Start monitoring to collect data.")

# ============================================
# TAB 4: POLICY ASSISTANT
# ============================================
with tab4:
    st.subheader("📚 Policy Assistant - RAG System")
    st.markdown("Ask questions about examination policies and get instant answers with source references.")
    
    # Example Questions
    st.markdown("**💡 Example Questions:**")
    example_cols = st.columns(4)
    examples = [
        ("📱 Is a smartwatch permitted?", "Is a smartwatch permitted during exams?"),
        ("👀 What about suspicious behavior?", "What should I do for suspicious behavior?"),
        ("📄 How to report incidents?", "How do I report an incident?"),
        ("📚 What items are prohibited?", "What items are prohibited in exams?")
    ]
    
    for i, (label, question) in enumerate(examples):
        with example_cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.policy_query = question
    
    # Query Input
    query = st.text_input(
        "Your question:",
        placeholder="e.g., Is a smartwatch permitted during exams?",
        value=st.session_state.get('policy_query', '')
    )
    
    if query:
        with st.spinner("🔍 Searching policies..."):
            results = rag.semantic_search(query, top_k=5)
            
            if results:
                st.success(f"✅ Found {len(results)} relevant policies")
                
                for i, result in enumerate(results):
                    doc = result['document']
                    with st.expander(
                        f"📄 {doc['title']} (Relevance: {result['score']:.2f})",
                        expanded=i == 0
                    ):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Policy ID:** `{doc['id']}`")
                            st.markdown(f"**Category:** `{doc['category']}`")
                            st.markdown(f"**Content:** {doc['content']}")
                        with col2:
                            st.markdown("**Recommended Actions:**")
                            for action in doc.get('actions', ['Review policy']):
                                st.markdown(f"• {action}")
                            
                            if st.button("📋 Apply Policy", key=f"apply_{doc['id']}"):
                                st.success(f"Policy {doc['id']} applied to current session")
            else:
                st.warning("No relevant policies found. Try rephrasing your question.")
    
    # Browse All Policies
    with st.expander("📚 Browse All Policies", expanded=False):
        categories = list(set(p['category'] for p in rag.policies))
        selected_category = st.selectbox("Filter by Category", ["All"] + categories)
        
        filtered_policies = rag.policies if selected_category == "All" else [p for p in rag.policies if p['category'] == selected_category]
        
        for policy in filtered_policies:
            st.markdown(f"""
            <div class="policy-card">
                <div>
                    <span class="policy-title">{policy['title']}</span>
                    <span class="policy-category">{policy['category']}</span>
                </div>
                <p style="margin: 8px 0; color: #555; font-size: 0.9rem;">{policy['content'][:200]}...</p>
                <div style="font-size: 0.8rem; color: #888;">
                    <strong>Actions:</strong> {', '.join(policy.get('actions', ['Review']))}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# TAB 5: REPORTS & EVIDENCE
# ============================================
with tab5:
    st.subheader("📄 Reports & Evidence")
    
    tab5a, tab5b = st.tabs(["📋 Reports", "📸 Evidence"])
    
    with tab5a:
        if st.session_state.reports:
            for report in reversed(st.session_state.reports[-5:]):
                with st.expander(f"📊 Report: {report['report_id']} - {report['exam_id']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Generated:** {report['generated_at']}")
                        st.markdown(f"**Duration:** {report['duration']['total_minutes']:.1f} minutes")
                        st.markdown(f"**Total Events:** {report['total_events']}")
                        st.markdown(f"**Total Alerts:** {report['total_alerts']}")
                    with col2:
                        st.markdown(f"**Confirmed Violations:** {report['confirmed_violations']}")
                        st.markdown(f"**Dismissed Alerts:** {report['dismissed_alerts']}")
                        st.markdown(f"**Camera Status:** {report['camera_status']}")
                        st.markdown(f"**Total Frames:** {report['total_frames']}")
                    
                    st.markdown("---")
                    st.markdown("**Summary:**")
                    st.markdown(report['summary']['summary_text'])
                    
                    st.markdown("**Recommendations:**")
                    for rec in report['recommendations']:
                        st.markdown(f"• {rec}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Download JSON", key=f"json_{report['report_id']}"):
                            json_str = report_agent.export_report_json(report)
                            st.download_button(
                                "📥 Download JSON File",
                                json_str,
                                f"{report['report_id']}.json",
                                "application/json"
                            )
                    with col2:
                        if st.button("📥 Download CSV", key=f"csv_{report['report_id']}"):
                            csv_str = report_agent.export_report_csv(report)
                            st.download_button(
                                "📥 Download CSV File",
                                csv_str,
                                f"{report['report_id']}.csv",
                                "text/csv"
                            )
        else:
            st.info("No reports generated yet")
    
    with tab5b:
        if st.session_state.evidence:
            st.markdown(f"**Total Evidence Items:** {len(st.session_state.evidence)}")
            
            for ev in reversed(st.session_state.evidence[-10:]):
                st.markdown(f"""
                <div class="evidence-box">
                    <strong>Evidence ID:</strong> {ev['evidence_id']}<br>
                    <strong>Event:</strong> {ev['sub_type'].replace('_', ' ').title()}<br>
                    <strong>Time:</strong> {ev['timestamp']}<br>
                    <strong>Confidence:</strong> {ev['confidence']:.2f}<br>
                    <strong>Camera:</strong> {ev['metadata']['camera_id']}<br>
                    <strong>Exam:</strong> {ev['metadata']['exam_id']}<br>
                    <strong>Frame:</strong> {ev['metadata']['frame_number']}
                </div>
                """, unsafe_allow_html=True)
                st.divider()
        else:
            st.info("No evidence collected yet")

# ============================================
# TAB 6: AI AGENTS
# ============================================
with tab6:
    st.subheader("🤖 AI Agent Framework")
    st.markdown("Monitor the activity of all AI agents in the system.")
    
    # Agent Status Cards
    col1, col2 = st.columns(2)
    
    with col1:
        # Alert Agent
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4>🔔 Alert Agent</h4>
            <p><strong>Status:</strong> 🟢 Active</p>
            <p><strong>Alerts Generated:</strong> {}</p>
            <p><strong>Thresholds:</strong> High: ≥0.8, Medium: ≥0.6, Low: ≥0.4</p>
            <p><strong>Active Alerts:</strong> {}</p>
        </div>
        """.format(len(st.session_state.alerts), 
                  len([a for a in st.session_state.alerts if a.get('status') == 'active'])), 
        unsafe_allow_html=True)
        
        # Policy Agent
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4>📚 Policy Agent</h4>
            <p><strong>Status:</strong> 🟢 Active</p>
            <p><strong>Policies:</strong> {} policies loaded</p>
            <p><strong>Categories:</strong> {}</p>
            <p><strong>Queries Processed:</strong> {}</p>
        </div>
        """.format(len(rag.policies), 
                  len(set(p['category'] for p in rag.policies)),
                  len(st.session_state.get('policy_queries', []))),
        unsafe_allow_html=True)
    
    with col2:
        # Evidence Agent
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4>📸 Evidence Agent</h4>
            <p><strong>Status:</strong> 🟢 Active</p>
            <p><strong>Evidence Items:</strong> {}</p>
            <p><strong>Linked Events:</strong> {}</p>
            <p><strong>Storage:</strong> In-memory</p>
        </div>
        """.format(len(st.session_state.evidence),
                  len(set(e.get('event_id') for e in st.session_state.evidence))),
        unsafe_allow_html=True)
        
        # Report Agent
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <h4>📊 Report Agent</h4>
            <p><strong>Status:</strong> 🟢 Active</p>
            <p><strong>Reports Generated:</strong> {}</p>
            <p><strong>Export Formats:</strong> JSON, CSV</p>
            <p><strong>Last Report:</strong> {}</p>
        </div>
        """.format(len(st.session_state.reports),
                  st.session_state.reports[-1]['report_id'] if st.session_state.reports else 'None'),
        unsafe_allow_html=True)
    
    # Agent Activity Log
    st.markdown("---")
    st.subheader("📋 Agent Activity Log")
    
    if st.session_state.events:
        log_data = []
        for event in st.session_state.events[-10:]:
            log_data.append({
                'Time': event.get('timestamp', '')[:19],
                'Event': event.get('sub_type', 'unknown').replace('_', ' ').title(),
                'Confidence': f"{event.get('confidence', 0):.2f}",
                'Agent': 'Alert' if event.get('confidence', 0) > 0.6 else 'Monitor',
                'Action': 'Alert Generated' if event.get('confidence', 0) > 0.6 else 'Logged'
            })
        
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)
    else:
        st.info("No agent activity to display")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🎓 AI Classroom Monitoring System v2.0")
with col2:
    st.caption("⚡ Powered by Streamlit, RAG, & Multi-Agent AI")
with col3:
    if st.session_state.is_processing:
        st.caption("🟢 Live Monitoring Active")
    else:
        st.caption("⏸️ System Idle")

# ============================================
# AUTO-REFRESH FOR CONTINUOUS MONITORING - FIXED
# ============================================
if st.session_state.is_processing:
    time.sleep(0.5)
    st.rerun()  # FIXED: Changed from experimental_rerun to rerun