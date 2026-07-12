import streamlit as st
import joblib
import pandas as pd
import requests
import google.generativeai as genai
from PIL import Image

# ==========================
# Page Config
# ==========================
st.set_page_config(page_title="Agri-Pilot AI", page_icon="🌱", layout="wide")

# ==========================
# CSS for Glass-Panel Cards
# ==========================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
body { background: #f8f9fa; }

.glass-panel {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(16, 24, 40, 0.05);
  padding: 20px;
  margin-bottom: 16px;
}

.glass-panel h3 {
  margin-top: 0;
  color: #191c1d;
  font-weight: 600;
  font-size: 18px;
}

.stNumberInput input { 
  border-radius: 8px !important; 
  border: 1px solid #e5e7eb !important;
}

.stButton>button {
  background: linear-gradient(180deg, #22C55E, #006e2f) !important;
  color: #fff !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  border: none !important;
}

.stButton>button:hover {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3) !important;
}

.hitl-panel {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  margin-top: 24px;
  box-shadow: 0 -4px 12px rgba(16, 24, 40, 0.05);
}

.success-box {
  background: #ecfdf5;
  border-left: 4px solid #22C55E;
  padding: 12px;
  border-radius: 8px;
  color: #065f46;
  font-weight: 500;
  margin: 12px 0;
}

.report-box {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px;
  margin: 12px 0;
  line-height: 1.6;
  color: #374151;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ==========================
# API Setup
# ==========================
GEMINI_API_KEY = "AQ.Ab8RN6I75j6o1s5O6_el3cqT4iKka3bhmRBjF7xSrxmrOrRBug"
WEATHER_API_KEY = "90975180569205a4e2ba07948d0e3280"
genai.configure(api_key=GEMINI_API_KEY)


@st.cache_resource
def load_models():
    return joblib.load('crop_ann_model.pkl'), joblib.load('scaler_model.pkl')


model, scaler = load_models()


def get_weather(city_name):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url, timeout=8).json()
        return float(res.get("main", {}).get("temp", 20.8)), float(res.get("main", {}).get("humidity", 82.0))
    except Exception:
        return 20.8, 82.0


def generate_vision_report(prompt, image_obj):
    try:
        vision_model = genai.GenerativeModel('gemini-3.5-flash')
        response = vision_model.generate_content([prompt, image_obj])
        return response.text
    except Exception:
        try:
            vision_model = genai.GenerativeModel('gemini-3.1-pro')
            response = vision_model.generate_content([prompt, image_obj])
            return response.text
        except Exception as e:
            return f"Error generating vision report: {e}"


# ==========================
# Sidebar Weather
# ==========================
st.sidebar.title("🌍 Real-time Weather")
city = st.sidebar.text_input("Enter City:", value="Karachi")
temp, hum = get_weather(city)
st.sidebar.metric("Temperature", f"{temp}°C")
st.sidebar.metric("Humidity", f"{hum}%")

# ==========================
# State Initialization
# ==========================
if "pred_crop" not in st.session_state:
    st.session_state.pred_crop = None
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False
if "report_text" not in st.session_state:
    st.session_state.report_text = ""

# ==========================
# Main Title
# ==========================
st.title("🌱 Agri-Pilot: Smart Farming Co-Pilot")

# ==========================
# Two-Column Layout
# ==========================
col1, col2 = st.columns([1.5, 1])

# ===== COLUMN 1: Soil & Weather Analysis =====
with col1:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 🌾 Soil & Weather Analysis")
    
    N = st.number_input("Nitrogen (N)", value=90.0, min_value=0.0)
    P = st.number_input("Phosphorus (P)", value=42.0, min_value=0.0)
    K = st.number_input("Potassium (K)", value=43.0, min_value=0.0)
    temp_val = st.number_input("🌡️ Temperature (°C) [Live API]", value=float(temp))
    humidity_val = st.number_input("💧 Humidity (%) [Live API]", value=float(hum))
    ph = st.number_input("pH Level", value=6.5, min_value=0.0, max_value=14.0)
    rainfall = st.number_input("Rainfall (mm)", value=202.9, min_value=0.0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # STEP 1: Recommend Crop
    if st.button("🌱 Recommend Crop", key="recommend_btn"):
        with st.spinner("Analyzing soil and weather data..."):
            try:
                input_df = pd.DataFrame([[N, P, K, temp_val, humidity_val, ph, rainfall]],
                                        columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
                pred = model.predict(scaler.transform(input_df))[0]
                st.session_state.pred_crop = pred.upper()
                st.session_state.report_ready = False
                st.session_state.report_text = ""
                st.success(f"🎯 **Recommended crop: {st.session_state.pred_crop}**")
            except Exception as e:
                st.error(f"Prediction error: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ===== COLUMN 2: Plant Health =====
with col2:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 📸 Plant Health")
    
    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "png"])
    if uploaded_file:
        try:
            st.image(uploaded_file, width=300)
        except Exception as e:
            st.error(f"Image error: {e}")
    
    farmer_query = st.text_area("Farmer's Query:", "The leaves are wilting and brown.", height=100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # STEP 2: Generate Report (only if crop is predicted)
    if st.session_state.pred_crop:
        if st.button("📋 Generate AI Report", key="report_btn"):
            if uploaded_file is None:
                st.warning("⚠️ Please upload a leaf image first!")
            else:
                with st.spinner("🧠 AI Co-Pilot is analyzing..."):
                    try:
                        image = Image.open(uploaded_file)
                        prompt = f"Crop: {st.session_state.pred_crop}. Query: {farmer_query}. Provide a professional diagnostic report."
                        report_text = generate_vision_report(prompt, image)
                        st.session_state.report_text = report_text
                        st.session_state.report_ready = True
                        st.success("✅ Report generated!")
                    except Exception as e:
                        st.error(f"Report error: {e}")
    else:
        st.info("👆 Recommend a crop first, then generate a report.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# Report Display + HITL Panel
# ==========================
if st.session_state.report_ready:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.markdown("### 📋 AI Co-Pilot Diagnostic Report")
    st.markdown(f'<div class="report-box">{st.session_state.report_text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # HITL Panel
    st.markdown('<div class="hitl-panel">', unsafe_allow_html=True)
    st.markdown("### Review & Approval")
    
    action = st.radio("Review Action:", ["Pending", "✅ Approve", "❌ Reject"], horizontal=True)
    
    if action == "✅ Approve":
        st.balloons()
        st.success("✅ Report officially approved! Ready for distribution.")
        st.download_button(label="📄 Download Report", data=st.session_state.report_text, file_name="AgriPilot_Report.txt")
    
    elif action == "❌ Reject":
        st.error("❌ Report Rejected by Agronomist. This report is blocked from being downloaded.")
        feedback = st.text_area("Reason for Rejection (Internal Use Only):", placeholder="E.g., AI identified the wrong plant species...")
        
        if st.button("📤 Submit Review"):
            if feedback.strip() == "":
                st.warning("⚠️ Please enter a reason before submitting.")
            else:
                st.success("🙏 Thanks for your review! Your feedback has been recorded to improve our AI.")
                st.info("🔄 Please adjust the inputs or upload a clearer image, and run the analysis again.")
    
    st.markdown("</div>", unsafe_allow_html=True)
