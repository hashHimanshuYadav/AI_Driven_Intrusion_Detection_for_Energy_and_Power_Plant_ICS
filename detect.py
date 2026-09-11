import os
import time
import json
import joblib
import numpy as np
from tensorflow.keras.models import load_model

PROJECT_DIR = '/content/drive/MyDrive/AI-IDS_for_PowerPlant'
if os.path.exists(PROJECT_DIR):
    os.chdir(PROJECT_DIR)

STREAM_BUFFER_FILE = 'live_stream.json'

print("[-] Loading trained IDS models and scaler artifacts...")
try:
    rf_model = joblib.load('rf_powerplant_ids.pkl')
    iso_model = joblib.load('iso_powerplant_ids.pkl')
    scaler = joblib.load('scaler_powerplant_ids.pkl')
    lstm_model = load_model('lstm_powerplant_ids.keras')
    print("[+] Models online with calibrated OT voting logic.\n")
except FileNotFoundError as e:
    raise SystemExit(f"[!] Artifact error: {e}. Run training cell first.")

def analyze_packet(raw_features):
    scaled = scaler.transform(np.array(raw_features).reshape(1, -1))
    
    # 1. Random Forest probability
    rf_prob = float(rf_model.predict_proba(scaled)[0][1])
    
    # 2. Isolation Forest anomaly
    iso_hit = 1 if iso_model.predict(scaled)[0] == -1 else 0
    
    # 3. LSTM threat score
    lstm_prob = float(lstm_model.predict(scaled.reshape(1, 1, -1), verbose=0)[0][0])

    # Calibrated Detection Rules:
    # Rule A: Strong RF Signature (>= 80%) fires an alert (catches Replay, DoS, Insider attacks)
    # Rule B: Zero-Day Anomaly requires BOTH IsoForest and high LSTM agreement (>= 98%)
    threat_detected = (rf_prob >= 0.80) or (iso_hit == 1 and lstm_prob >= 0.98)

    return threat_detected, rf_prob, iso_hit, lstm_prob

last_processed_id = None
print("[*] Monitoring 'live_stream.json' (single process stream)...\n")

try:
    while True:
        if os.path.exists(STREAM_BUFFER_FILE):
            try:
                with open(STREAM_BUFFER_FILE, 'r') as f:
                    packet = json.load(f)

                if packet.get('packet_id') != last_processed_id:
                    last_processed_id = packet['packet_id']
                    
                    alert, rf_score, iso_flag, lstm_score = analyze_packet(packet['features'])
                    ts = packet['timestamp']
                    pid = packet['packet_id']
                    injected = packet.get('simulated_class', 'Unknown')

                    if alert:
                        print(f"[{ts}] [PACKET #{pid:04d}] [CRITICAL ALERT] Injected: {injected}")
                        print(f"       -> RF Prob: {rf_score*100:.1f}% | Iso Anomaly: {bool(iso_flag)} | LSTM Score: {lstm_score*100:.1f}%")
                        print("       -> PLAYBOOK ACTION: Isolate Workstation / Trip Safety Breaker Interlock\n")
                    else:
                        print(f"[{ts}] [PACKET #{pid:04d}] [OK] Normal Operation (Injected: {injected} | RF Score: {rf_score*100:.1f}%) -> Forwarded.\n")

            except (json.JSONDecodeError, PermissionError):
                pass

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[!] IDS engine stopped by operator.")
