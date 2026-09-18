# 🚗 DriverGuard AI

### AI-Powered Driver Drowsiness, Yawning & Distraction Detection System

DriverGuard AI is a real-time computer vision system designed to monitor driver alertness and attention using a camera.

The system analyzes facial landmarks to detect signs of:

- 😴 Driver drowsiness
- 🥱 Yawning
- 👀 Visual distraction
- ↔️ Head direction
- ⚠️ Unsafe driving conditions

It combines these indicators into a **Driver Safety Score** and presents the results through an interactive dashboard.

---

## ✨ Features

### 🧠 Real-Time AI Monitoring

DriverGuard AI continuously analyzes the driver's face using computer vision and facial landmarks.

### 😴 Drowsiness Detection

The system uses **Eye Aspect Ratio (EAR)** to estimate whether the driver's eyes remain closed for an extended period.

It identifies:

- `DRIVER ALERT`
- `GETTING DROWSY`
- `CRITICAL DROWSINESS`

### 🥱 Yawning Detection

The system analyzes mouth opening using facial landmarks to identify prolonged mouth opening associated with yawning.

### 👀 Distraction Detection

DriverGuard AI monitors head direction and identifies:

- Looking Left
- Looking Right
- Looking Down
- Looking Up
- Forward

Prolonged deviation from the forward direction can trigger distraction warnings.

### 📊 Driver Safety Score

Multiple driving indicators are combined into a single safety score ranging from:

`0 – 100`

The score is used to categorize the driver's current condition as:

- 🟢 Safe
- 🟡 Caution
- 🔴 High Risk

### 🌐 Interactive Dashboard

A Streamlit-based dashboard is being developed to provide a passenger-friendly interface containing:

- Live driver camera
- Driver condition
- Safety score
- Alertness status
- Attention status
- Yawning status
- Head direction
- Journey information
- Emergency assistance

### 🚨 Emergency Assistance

The dashboard includes a **GET HELP** concept that allows the passenger to contact a predefined emergency contact when an unsafe condition occurs.

The current prototype uses a phone-call interface, while backend-based SMS/voice notification integration can be added in future development.

---

# 🏗️ System Architecture

```text
                ┌───────────────────┐
                │   Camera Input    │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Face Detection &  │
                │ Facial Landmarks  │
                └─────────┬─────────┘
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
        Eye Analysis   Mouth Analysis  Head Analysis
          (EAR)           (Yawning)     (Direction)
             │            │            │
             └────────────┼────────────┘
                          ▼
                ┌───────────────────┐
                │ Driver Monitoring │
                │     Engine        │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Safety Score &    │
                │ Risk Assessment   │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Streamlit Web     │
                │    Dashboard      │
                └─────────┬─────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
          Driver Alerts       Emergency Help

## 📸 Dashboard Preview

<p align="center">
  <img src="screenshots/dashboard1.png" alt="DriverGuard AI Dashboard" width="900">
</p>
<p align="center">
  <img src="screenshots/dashboard2.png" alt="DriverGuard AI Dashboard" width="900">
</p>
