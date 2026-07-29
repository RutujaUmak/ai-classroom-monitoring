# ============================================
# CELL: Real-time Status Check
# ============================================

import requests
import json
from datetime import datetime

print("📊 APP STATUS DASHBOARD")
print("=" * 70)
print(f"🕐 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Check main app
try:
    response = requests.get('http://localhost:8501', timeout=3)
    print(f"✅ App Status:   LIVE (HTTP {response.status_code})")
except:
    print("❌ App Status:   OFFLINE")

# Check external URL
try:
    response = requests.get('http://34.125.139.47:8501', timeout=3)
    print(f"✅ External URL: LIVE (HTTP {response.status_code})")
except:
    print("❌ External URL: OFFLINE")

# Check process
import subprocess
result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True)
if result.stdout:
    pids = result.stdout.decode().strip().split('\n')
    print(f"✅ Streamlit PID: {', '.join(pids)}")
else:
    print("❌ Streamlit NOT RUNNING")

print("=" * 70)
print("\n🌐 OPEN YOUR APP:")
print("   http://34.125.139.47:8501")
print("=" * 70)