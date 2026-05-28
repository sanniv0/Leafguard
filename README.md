# 🌿 Plant Disease Detector

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?logo=react)](https://reactjs.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.19.0-FF6F00?logo=tensorflow)](https://tensorflow.org)
[![Accuracy](https://img.shields.io/badge/Accuracy-96.99%25-brightgreen)](https://github.com)

A decoupled, production-ready deep learning application designed to detect diseases in plants (Pepper, Potato, Tomato) using a custom-trained **MobileNetV2** model. Featuring a modern glassmorphic React dashboard and a high-performance FastAPI inference engine.

---

## 🏗️ Architecture

This project has transitioned from a monolithic prototype to a modern **Decoupled Architecture**:

1.  **Backend (Inference Engine)**: A FastAPI server that loads the `best_model.keras` and provides a REST API for image classification.
2.  **Frontend (Botanical Observatory)**: A sleek React application built with Vite, featuring glassmorphism, real-time scanning animations, and detailed botanical advice.
3.  **Prototype (Legacy/Quick Test)**: A Streamlit-based interface for rapid testing and model validation.

---

## 📊 Dataset & Model Overview

The model was trained on a robust dataset of plant leaf images to ensure high reliability across various conditions.

### **Supported Classes**
- **Pepper**: Bacterial Spot, Healthy
- **Potato**: Early Blight, Late Blight, Healthy
- **Tomato**: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy

### **Model Specs**
- **Base Model:** `MobileNetV2`
- **Validation Accuracy:** **96.99%**
- **Inference Speed:** ~150ms per image

---

## 🛠️ Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js & npm
- Virtual Environment (recommended)

### 2. Backend Setup (FastAPI)
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn tensorflow pillow numpy

# Start the server
python server.py
```
*The API will be available at `http://127.0.0.1:8000`*

### 3. Frontend Setup (React)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The dashboard will be available at `http://localhost:5173`*

### 4. Prototype Setup (Streamlit)
```bash
# From the root directory
streamlit run app.py
```

---

## 📂 Project Structure
```text
CNN_Project_Kaggle/
├── frontend/            # React + Vite application
│   ├── src/             # Dashboard logic & Glassmorphic UI
│   └── ...
├── server.py            # FastAPI Inference Engine
├── app.py               # Streamlit Prototype
├── best_model.keras     # Trained MobileNetV2 Model
├── model.ipynb          # Training & Evaluation Notebook
└── README.md            # You are here!
```

---

*Developed with ❤️ for Sustainable Agriculture.*
