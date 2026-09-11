import os
import time
import json
import joblib
import pandas as pd
import numpy as np

PROJECT_DIR = '/content/drive/MyDrive/AI-IDS_for_PowerPlant'
if os.path.exists(PROJECT_DIR):
    os.chdir(PROJECT_DIR)

STREAM_BUFFER_FILE = 'live_stream.json'

# Load the authentic raw dataset
import glob
csv_file = [f for f in glob.glob('*.csv') if any(k in f.lower() for k in ['energy', 'cyber', 'power'])][0]
df = pd.read_csv(csv_file)

target_col = [col for col in df.columns if any(k in col.lower() for k in ['attack', 'label', 'class', 'target'])][0]
classes = df[target_col].unique().tolist()

# Drop identifier columns just like in training
cols_to_drop = [c for c in df.columns if any(k in c.lower() for k in ['id', 'timestamp', 'time', 'ip', 'index'])]
cols_to_drop = [c for c in cols_to_drop if c != target_col]
df = df.drop(columns=cols_to_drop, errors='ignore')

# Pre-convert object columns with saved LabelEncoders
for col in df.select_dtypes(include=['object']).columns:
    if col != target_col:
        df[col] = df[col].astype('category').cat.codes

print(f"[*] Authentic Telemetry Generator Ready across {len(classes)} classes.")
print("[*] Streaming exactly 1 packet every 2 seconds...\n")

packet_id = 1
try:
    while True:
        # Pull an authentic record from the real dataset
        sample = df.sample(n=1).iloc[0]
        actual_class = str(sample[target_col])
        features = sample.drop(labels=[target_col]).values.astype(float).tolist()

        payload = {
            "packet_id": packet_id,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "simulated_class": actual_class,
            "features": features
        }

        # Write safely
        temp = STREAM_BUFFER_FILE + '.tmp'
        with open(temp, 'w') as f:
            json.dump(payload, f)
        os.replace(temp, STREAM_BUFFER_FILE)

        print(f"[PACKET #{packet_id:04d}] {payload['timestamp']} | Telemetry Type: {actual_class}")
        packet_id += 1
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\n[!] Generator stopped.")
