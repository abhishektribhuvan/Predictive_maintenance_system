
<h1 align="center">⚙️ IoT Anomaly Detection System</h1>

<p align="center">
  <b>A real-time, distributed machine health monitoring system using ESP32, MPU6050 vibration sensor, Isolation Forest ML, and a Streamlit dashboard.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/ESP32-PlatformIO-orange?logo=espressif&logoColor=white" alt="ESP32"/>
  <img src="https://img.shields.io/badge/scikit--learn-IsolationForest-F7931E?logo=scikitlearn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

---

## 📖 What is This?

This project is an **end-to-end IoT anomaly detection system** that monitors industrial machine health in real-time. It collects vibration and temperature data from physical sensors, sends it to a backend server, trains a machine learning model to learn "normal" behavior, and then **detects anomalies** — unusual vibrations that could mean a machine is about to fail.

> **Think of it like a doctor's check-up for machines.** The sensor constantly measures the machine's "heartbeat" (vibrations), and the AI model flags when something feels "off".

---

## 🏗️ System Architecture

<p align="center">
  <img src="assets/architecture.png" alt="System Architecture" width="90%"/>
</p>

The system has **4 main components** that work together:

| # | Component | Technology | What it Does |
|---|-----------|-----------|--------------|
| 1 | **Sensor Hardware** | ESP32 + MPU6050 | Reads vibration & temperature data from the machine |
| 2 | **Backend API** | FastAPI (Python) | Receives sensor data, stores it, trains ML models, runs predictions |
| 3 | **ML Model** | Isolation Forest (scikit-learn) | Learns what "normal" looks like, detects anomalies |
| 4 | **Web Dashboard** | Streamlit (Python) | Visual dashboard to monitor machines, view graphs, trigger actions |

### 🔄 How Data Flows

```
ESP32 Sensor  ──HTTP POST──▶  FastAPI Server  ──saves──▶  CSV Database
                                    │
                              ┌─────┴─────┐
                              │  /train    │  ──▶  Trains Isolation Forest Model
                              │  /predict  │  ──▶  Returns Normal / Anomaly
                              └─────┬─────┘
                                    │
                            Streamlit Dashboard  ──▶  Shows charts, status, alerts
```

---

## 📁 Project Structure

```
Anomaly Detection System/
│
├── 📂 Firmware/                    # ESP32 microcontroller code
│   ├── src/
│   │   └── main.cpp                # Sensor reading + WiFi data transmission
│   ├── platformio.ini              # PlatformIO build configuration
│   └── lib/                        # External libraries (MPU6050, ArduinoJson, etc.)
│
├── 📂 backend/                     # Python backend server
│   ├── app.py                      # FastAPI REST API (receive data, train, predict)
│   ├── web_app.py                  # Streamlit dashboard (monitoring UI)
│   ├── training.py                 # Standalone model training script
│   ├── machine_data.json           # Sample machine data
│   └── vibration_model.pkl         # Trained ML model file
│
├── 📂 database/                    # Collected sensor data
│   └── training_data.csv           # Historical vibration + temperature readings
│
└── 📂 assets/                      # README images
    ├── banner.png
    └── architecture.png
```

---

## ⚡ Features

### 🔧 Hardware (ESP32 Firmware)
- **MPU6050 accelerometer** reads X, Y, Z vibration data at 10 Hz
- Computes **mean magnitude** and **variance** from 10 samples per cycle
- Reads **temperature** from the onboard sensor
- Sends data as **JSON over WiFi** (HTTP POST) to the backend
- **WiFiManager** portal — no hardcoded WiFi credentials, configure via phone/laptop
- Uses MAC address as a unique **device identifier** for multi-machine support

### 🖥️ Backend API (FastAPI)
- `POST /send_from_esp32` — Receives sensor data from any ESP32 device and saves to per-device CSV
- `GET /train/{device_id}` — Trains an **Isolation Forest** model on collected data (requires 500+ rows)
- `GET /predict_latest/{device_id}` — Predicts if the latest reading is **Normal** or **Anomaly**
- Supports **multiple devices** — each device gets its own data file and model

### 📊 Dashboard (Streamlit)
- **Home Page** — Overview of all connected machines with real-time status cards
- **Machine Details** — Drill-down view with metrics (mean, variance, temperature) and health status
- **Model Retraining** — One-click model retraining from the dashboard
- **Advanced Analytics** — Interactive graphs (Time vs Mean, Time vs Variance, Anomaly-Aware)
- **Add New Machine** — Register new devices with custom names
- **Search & Filter** — Find machines by ID or name
- **Dark/Light Theme** — Toggle between themes in Settings

---

## 🚀 Getting Started

### Prerequisites

| Tool | Purpose | Install Guide |
|------|---------|---------------|
| **Python 3.9+** | Backend & Dashboard | [python.org](https://www.python.org/downloads/) |
| **PlatformIO** | ESP32 firmware upload | [platformio.org](https://platformio.org/install) |
| **ESP32 Board** | Microcontroller | Any ESP32 DevKit |
| **MPU6050 Sensor** | Accelerometer / Gyro | Wired via I2C (SDA=GPIO21, SCL=GPIO22) |

### 1️⃣ Install Python Dependencies

```bash
pip install fastapi uvicorn pandas scikit-learn joblib streamlit requests
```

### 2️⃣ Start the Backend API

```bash
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at **http://localhost:8000**. You can check the auto-generated docs at **http://localhost:8000/docs**.

### 3️⃣ Start the Streamlit Dashboard

Open a **new terminal** and run:

```bash
cd backend
streamlit run web_app.py
```

The dashboard will open in your browser at **http://localhost:8501**.

### 4️⃣ Flash the ESP32 Firmware

1. Open the `Firmware/` folder in **VS Code** with the PlatformIO extension
2. Update the `serverUrl` in `src/main.cpp` with your computer's **local IP address**:
   ```cpp
   const char* serverUrl = "http://<YOUR_PC_IP>:8000/send_from_esp32";
   ```
3. Connect your ESP32 via USB and click **Upload** in PlatformIO
4. Open Serial Monitor (115200 baud) to see sensor readings
5. On first boot, connect to the **"ESP32-Setup-Portal"** WiFi network and enter your WiFi credentials

### 5️⃣ Wire the MPU6050 Sensor

```
MPU6050     →     ESP32
───────────────────────
VCC         →     3.3V
GND         →     GND
SDA         →     GPIO 21
SCL         →     GPIO 22
```

---

## 🧠 How the ML Model Works

### Isolation Forest — Explained Simply

> **Imagine you have a forest of decision trees.** Each tree randomly picks a feature and a split point, trying to "isolate" each data point. **Normal data** is similar to other points, so it takes **many splits** to isolate. **Anomalies** are weird and different, so they get isolated **quickly** in just a few splits.

#### Training Phase
1. The ESP32 sends hundreds of vibration readings (mean & variance) to the server
2. When you have **500+ data points**, you trigger training via the dashboard or API
3. The Isolation Forest learns the "shape" of normal vibration patterns
4. The trained model is saved as a `.pkl` file for future predictions

#### Prediction Phase
1. A new reading comes in from the sensor
2. The model scores how "anomalous" the reading is
3. If the score indicates isolation in few splits → **🚨 Anomaly Detected!**
4. If the score indicates normal behavior → **✅ Normal**

### Key Parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `n_estimators` | 100 | Number of trees in the forest |
| `contamination` | 0.01 | Expects ~1% of data to be anomalies |
| `features` | `[mean, var]` | Uses vibration mean and variance |

---

## 🔌 API Reference

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| `GET` | `/` | Health check | `curl http://localhost:8000/` |
| `POST` | `/send_from_esp32` | Send sensor data | See below |
| `GET` | `/train/{device_id}` | Train model for device | `curl http://localhost:8000/train/ESP-AA:BB:CC:DD:EE:FF` |
| `GET` | `/predict_latest/{device_id}` | Get latest prediction | `curl http://localhost:8000/predict_latest/ESP-AA:BB:CC:DD:EE:FF` |

### Example: Sending Sensor Data

```bash
curl -X POST http://localhost:8000/send_from_esp32 \
  -H "Content-Type: application/json" \
  -d '{"mac_id": "ESP-AA:BB:CC:DD:EE:FF", "mean": 9.81, "var": 0.002, "temp": 33.5}'
```

### Example: Prediction Response

```json
{
  "machine_id": "ESP-AA:BB:CC:DD:EE:FF",
  "mean": 9.81,
  "var": 0.002,
  "temp": 33.5,
  "is_anomaly": false,
  "status": "Normal"
}
```

---

## 📸 Dashboard Screenshots
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/00801a72-c45d-4779-911f-e4b3b7c499b1" />
<img width="1918" height="942" alt="image" src="https://github.com/user-attachments/assets/fd125ae0-7952-489a-8958-8e33ac44b75c" />



The Streamlit dashboard provides:

| View | Description |
|------|-------------|
| 🏠 **Home** | Grid of machine cards showing status (active/inactive) and health (normal/anomaly) |
| 🔍 **Machine Details** | Drill-down with real-time metrics, progress bars, and model retraining |
| 📈 **Analytics** | Line charts for Mean, Variance, and Anomaly-Aware graphs |
| ⚙️ **Add Machine** | Form to register new ESP32 devices with custom names |
| 🎛️ **Settings** | Dark/Light theme toggle |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Sensor** | ESP32 + MPU6050 | Low-cost, WiFi-enabled microcontroller with precise accelerometer |
| **Firmware** | Arduino / PlatformIO | Industry-standard for embedded IoT development |
| **Networking** | WiFi + HTTP/JSON | Simple, reliable, no extra broker needed |
| **Backend** | FastAPI | Fast, modern, auto-docs, async-ready Python framework |
| **ML** | Isolation Forest (scikit-learn) | Perfect for unsupervised anomaly detection — no labeled data needed |
| **Storage** | CSV files | Lightweight, no database setup required |
| **Frontend** | Streamlit | Rapid Python-based dashboards with zero frontend code |

---

## 🤔 FAQs

<details>
<summary><b>Q: Do I need labeled "anomaly" data to train the model?</b></summary>
<br>
<b>No!</b> Isolation Forest is an <b>unsupervised</b> algorithm. You only need to collect normal operating data. The model figures out anomalies on its own by detecting data points that are statistically different from the norm.
</details>

<details>
<summary><b>Q: How many data points do I need before training?</b></summary>
<br>
The system requires a <b>minimum of 500 data points</b> before you can train. Since the ESP32 sends data every ~1 second, this means about <b>8-9 minutes</b> of continuous data collection.
</details>

<details>
<summary><b>Q: Can I use multiple ESP32 sensors at the same time?</b></summary>
<br>
<b>Yes!</b> The system is fully <b>distributed</b>. Each ESP32 sends its unique MAC address as an identifier. The backend creates separate data files and models for each device. The dashboard shows all machines in a unified view.
</details>

<details>
<summary><b>Q: What kind of anomalies can it detect?</b></summary>
<br>
It detects <b>vibration anomalies</b> — any significant deviation in mean vibration magnitude or variance from the trained baseline. This could indicate: bearing failures, misalignment, imbalance, looseness, or other mechanical faults.
</details>

<details>
<summary><b>Q: Do I need to be on the same WiFi network?</b></summary>
<br>
<b>Yes</b>, for the default setup. The ESP32 sends data directly to the FastAPI server on your local network. For remote access, you can deploy the backend to a cloud server and update the <code>serverUrl</code> in the firmware.
</details>

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built with ❤️ by Abhishek</b>
  <br><br>
  ⭐ If you found this useful, please give it a star!
</p>
