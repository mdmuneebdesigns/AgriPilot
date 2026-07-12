# 🌱 Smart Agri-Pilot for Industry

## Overview
Agri-Pilot is an AI Co-Pilot designed to assist Agronomists and farmers in diagnosing crop health. It combines a traditional Predictive Deep Learning model with cutting-edge Generative AI (LLMs) to process multimodal data and provide actionable insights with a Human-in-the-Loop workflow.

## 🎯 Hackathon Requirements Fulfilled

* **Multimodal Data Processing:** The system processes Tabular data (Soil N, P, K, Temp, Humidity), Text data (Farmer's complaint), and Image data (Crop leaf visual inspection).
* **Predictive Deep Learning Engine:** Uses a Multi-Layer Perceptron (ANN) model trained on a Kaggle dataset of 2200 rows to accurately predict the best crop for the given soil parameters.
* **Generative AI Reasoning:** Integrates Google Gemini Pro Vision API to analyze the ANN output, farmer's text, and uploaded image to generate a professional diagnostic report.
* **Human-in-the-Loop (HITL):** Agronomists must explicitly review, modify, or approve the AI's recommendation before finalization.
* **Explainable AI:** Displays the Deep Learning model's confidence and clear reasoning for its choices.
* **Downloadable Report:** Generates a downloadable text/PDF report upon HITL approval.

## 🚀 How to Run the App

1. Install all dependencies:
   ```bash
   pip install -r requirements.txt