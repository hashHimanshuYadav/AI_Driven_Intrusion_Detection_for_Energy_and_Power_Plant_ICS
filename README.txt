# AI-Driven Intrusion Detection System for Power Plant ICS 🏭⚡

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Latest-lightgrey)
![Domain](https://img.shields.io/badge/Domain-OT%2FICS%20Cybersecurity-red)

An advanced, real-time Intrusion Detection System (IDS) designed specifically for Industrial Control Systems (ICS) and Operational Technology (OT) environments. This project monitors power plant telemetry and smart grid network traffic to detect malicious injections (e.g., S7comm wiping, IEC 61850 MITM) and prevent cascading physical failures.

---

## 📖 Project Overview
Traditional IT firewalls fail in OT environments because they do not understand industrial protocols or the physics of power plant telemetry. This project bridges that gap by deploying a multi-layered AI ensemble that monitors continuous sensor streams. 

The system relies on a **Consensus Voting Engine** to minimize false positives—ensuring that critical infrastructure is not unnecessarily shut down during normal operational transients, while reacting instantly to genuine cyber threats.

---

## 📊 Dataset & Justification
**Dataset:** [Distributed Energy Cybersecurity Dataset (Kaggle)](https://www.kaggle.com/datasets/colabsss/distributed-energy-cybersecurity-dataset)

**Why this dataset?**
Many cybersecurity projects rely on outdated IT-centric datasets (like NSL-KDD or CICIDS). However, those datasets only reflect standard web traffic (HTTP, TCP, UDP). 
To build an IDS for a *power plant*, the AI must understand physical metrics. This specific dataset was selected because it contains:
* **Authentic ICS Protocols:** Features mapped to industrial communication standards.
* **Physical Telemetry:** Represents actual sensor readings, voltage frequencies, and actuator commands.
* **Domain-Specific Attacks:** Includes targeted False Data Injections (FDI), Command Injections, and Reconnaissance scans designed specifically to manipulate smart grids and Programmable Logic Controllers (PLCs).

---

## 🧠 Machine Learning Architecture

The detection engine utilizes three distinct algorithms operating in parallel:

1. **Random Forest (Supervised):** Rapidly matches incoming packet features against known attack signatures.
2. **Isolation Forest (Unsupervised):** Profiles baseline "normal" plant operations. Flags unprecedented zero-day deviations that lack prior signatures.
3. **LSTM Recurrent Neural Network (Deep Learning):** Analyzes time-series telemetry to catch gradual, multi-stage attacks that unfold over continuous operational sequences.

**Decision Logic:** The engine uses a 2-out-of-3 consensus voting threshold (e.g., strict agreement between Isolation Forest and LSTM, or highly decisive Random Forest probability) to trigger the defense playbook.

---

## 🔄 The Telemetry Simulation Engine
Since physical SCADA networks are air-gapped and difficult to access for testing, this project includes a custom **Fake Data Generator** (`stream_generator.py`).

* **How it works:** It acts as a digital twin of a power plant's sensor array. It samples raw telemetry vectors from the dataset and injects them into a live buffer (`live_stream.json`) exactly every 2 seconds.
* **Real-Time Validation:** It randomly cycles between `Normal` baseline operations and specific cyberattacks (e.g., `DoS`, `Insider_Threat`), allowing the `detect.py` engine to be tested as if it were sitting on a live industrial network switch.

---

## 📂 Repository Structure

.
├── AI-Driven_Intrusion_Detection.ipynb   # Full training pipeline, data preprocessing, and visual analytics
├── stream_generator.py                   # Generates live multi-class telemetry packets
├── detect.py                             # Real-time IDS inference engine
├── more files could be added in the future --
├── .env                                  # (Git-ignored) Stores Kaggle API token
├── .gitignore                            # Prevents credential and large binary leakage
└── Saved_Models/                         # (Generated locally during runtime)
    ├── rf_powerplant_ids.pkl             # Serialized Random Forest
    ├── iso_powerplant_ids.pkl            # Serialized Isolation Forest
    ├── scaler_powerplant_ids.pkl         # Fitted StandardScaler
    └── lstm_powerplant_ids.keras         # Saved Deep Learning model
