# ✚ MEDIMIND — AI Clinical Decision Support & Health Analytics Platform

![MEDIMIND Platform](https://img.shields.io/badge/Platform-MEDIMIND-15b89a?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![Gemini AI](https://img.shields.io/badge/AI_Copilot-Google_Gemini_3.6-4285F4?style=for-the-badge&logo=google)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?style=for-the-badge&logo=mongodb)

**MEDIMIND** is an advanced AI-powered clinical decision-support ecosystem and patient analytics platform designed for healthcare professionals, clinical decision-makers, and patients. It integrates machine learning disease risk prediction models, real-time telemetry, Google Gemini AI clinical insights, automated PDF report generation, and organizational domain whitelisting.

---

## 🌟 Key Features

### 1. 📊 Interactive Clinical Dashboard
- Real-time patient telemetry counters (Total Patients, Executed Diagnostic Runs, High Risk Cases, Positive Risk Ratio).
- Dynamic risk distribution chart powered by custom conic-gradient visualizations.
- Highlights section for ML model accuracy status, Gemini AI online status, and PDF report readiness.

### 2. 🧪 Machine Learning Disease Risk Classifier
- Scikit-Learn trained diabetes prediction classifier (`disease_model.pkl`).
- Evaluates clinical parameters: **Glucose, Blood Pressure, BMI, Age, Diabetes Pedigree Function, Pregnancies, Insulin, and Skin Thickness**.
- Computes real-time confidence percentages, risk score scale (0–100), and risk categories (*Low, Moderate, High*).

### 3. 🤖 Google Gemini AI Clinical Assistant
- Powered by **Google Gemini 3.6 Flash** (`gemini-3.6-flash`).
- Provides real-time conversational clinical decision support, symptom explanations, over-the-counter treatment advice, and diagnostic rationale.
- Interactive multi-turn chat interface with message history and formatted response blocks.

### 4. 👤 Patient Self-Analysis & Registry
- Dedicated **Self Analysis** workflow allowing patients to conduct self-evaluations.
- Patient health metrics and prediction scores are automatically saved to their profile and made accessible to attending doctors and administrators.
- **Strict Data Isolation:** Patients see only their own health records and metrics, while Doctors and Admins access full clinical registries.

### 5. 📜 Diagnostic History & Automated PDF Reports
- Historical log of diagnostic evaluations, confidence metrics, and patient risk profiles.
- Automated clinical report generation formatting diagnostic metrics, AI rationale, and recommended follow-up tests.

### 6. 🛡️ Doctor Domain Whitelisting
- Administrative security portal allowing doctors and admins to manage and whitelist approved medical institution domains (`hospital.com`, `clinic.org`).
- Restricts doctor account registrations to whitelisted email domains.

---

## 📁 Repository Structure

```
Medimind/
├── backend/
│   ├── app.py                     # FastAPI REST API routes & lifespan initialization
│   ├── config.py                  # Pydantic environment configuration & settings
│   ├── database/
│   │   └── mongodb.py             # Async Motor / PyMongo database connection handler
│   ├── models/                    # Pydantic schemas (User, Patient, Prediction, Admin)
│   ├── services/                  # Business logic services
│   │   ├── database_service.py    # MongoDB queries & patient/prediction persistence
│   │   ├── prediction_service.py  # ML model loader & inference engine
│   │   ├── risk_service.py        # Risk score calculation & evaluation
│   │   ├── gemini_service.py      # Google Gemini 3.6 Flash integration
│   │   └── report_service.py      # Clinical PDF report builder
│   ├── trained_models/            # Serialized ML model (disease_model.pkl)
│   └── utils/                     # Auth JWT utilities, password hashing, and logging
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # SPA routing, Layout, and Views
│   │   ├── index.css              # Custom medical UI design system & tokens
│   │   └── main.jsx               # React entrypoint
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── datasets/                      # Training dataset (diabetes.csv)
├── requirements.txt               # Backend Python dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python:** `3.11` or higher
- **Node.js:** `18.x` or `20.x`
- **MongoDB:** Local instance on `mongodb://localhost:27017` or MongoDB Atlas URI

---

### 1. Clone the Repository
```bash
git clone https://github.com/YuviPa-cypher/Medimind-AI.git
cd Medimind-AI
```

---

### 2. Backend Setup
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your `.env` configuration file:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to configure your `MONGODB_URI` and your `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/).*

4. Start the FastAPI backend server:
   ```bash
   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload
   ```
   *Backend API will be running at:* `http://localhost:8001`

---

### 3. Frontend Setup
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *Frontend Application will be running at:* `http://localhost:5173`

---

## ⚡ Deploying to Vercel

This repository is pre-configured for **1-click single-repository Vercel deployment** (`vercel.json` + `api/index.py`).



## 🔑 Demo Login Credentials (Seeded on First Run)

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Doctor / Admin** | `doctor@medimind.com` | `doctor123` | Full access to Dashboard, Patients Registry, Analysis, History, AI Assistant, and Domain Whitelisting |
| **Patient** | Register a new account under **Patient** tab | *(User defined)* | Self-Analysis, Personal History, and Gemini AI Assistant |

---

## 🛡️ License

Distributed under the **MIT License**. See `LICENSE` for details.

