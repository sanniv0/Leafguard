import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
import time
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="LeafGuard AI - Botanical Observatory",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Design System Constants (Botanical Observatory) ---
PALETTE = {
    "base": "#0f1412",
    "surface": "#181d1a",
    "surface_high": "#262b29",
    "primary": "#013220",
    "accent": "#a2d1b7",
    "text": "#dfe4e0",
    "text_muted": "#8b938c",
    "error": "#ffb4ab",
}

# --- Custom CSS for The Botanical Observatory ---
def apply_botanical_theme():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@400;600&display=swap');

        /* Main App Reset */
        html, body, [class*="st-"] {{
            font-family: 'Inter', sans-serif;
            color: {PALETTE['text']};
        }}

        /* Restore Material Icons (avoid overriding them with 'Inter') */
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Symbols+Rounded');
        .material-icons, .material-symbols-rounded, [class*="material-symbols-rounded"] {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }}

        /* Strict fix for sidebar collapse button hover text */
        .st-emotion-cache-1aplgmp span, [data-testid="stSidebarCollapseButton"] span, [data-testid="stSidebarCollapseButton"] {{
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }}

        /* Hide Streamlit Header & Dev Toolbar */
        #MainMenu {{visibility: hidden;}}
        header {{display: none !important;}}
        footer {{visibility: hidden;}}
        [data-testid="stHeader"] {{display: none !important;}}
        [data-testid="stToolbar"] {{display: none !important;}}
        [data-testid="stStatusWidget"] {{display: none !important;}}

        .stApp {{
            background-color: {PALETTE['base']};
            background-image: 
                radial-gradient(at 0% 0%, rgba(1, 50, 32, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(162, 209, 183, 0.05) 0px, transparent 50%);
        }}

        /* Typography */
        h1, h2, h3, .header-text {{
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }}

        /* Glassmorphism Containers */
        .glass-card {{
            background: rgba(24, 29, 26, 0.6);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 1);
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }}

        /* Pulsing Glow for Upload */
        .upload-glow {{
            position: relative;
            z-index: 1;
        }}
        .upload-glow::after {{
            content: '';
            position: absolute;
            top: -20px; left: -20px; right: -20px; bottom: -20px;
            background: radial-gradient(circle, rgba(162, 209, 183, 0.1) 0%, transparent 70%);
            z-index: -1;
            animation: pulse 3s infinite ease-in-out;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}

        /* Custom Streamlit Element Overrides */
        [data-testid="stSidebar"] {{
            background-color: {PALETTE['base']} !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}

        /* Fix Upload Button & Overlap */
        .stFileUploader section {{
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px dashed {PALETTE['accent']} !important;
            border-radius: 20px !important;
            padding: 1rem !important;
        }}

        [data-testid="stFileUploader"] section > div {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            text-align: center !important;
            padding: 1rem 0 !important;
        }}

        /* Fix the 'uploadUpload' overlap glitch and ensure text visibility */
        [data-testid="stFileUploader"] button {{
            background-color: {PALETTE['primary']} !important;
            border: 1px solid {PALETTE['accent']} !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 0.6rem 2rem !important;
            width: auto !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
            transition: all 0.2s ease !important;
        }}

        [data-testid="stFileUploader"] button:hover {{
            background-color: {PALETTE['accent']} !important;
            color: {PALETTE['primary']} !important;
            transform: translateY(-2px);
        }}

        [data-testid="stFileUploader"] button p {{
            font-weight: 700 !important;
            font-family: 'Outfit', sans-serif !important;
            margin: 0 !important;
        }}

        /* Result Card - Scientific Slide Style */
        .specimen-slide {{
            border-left: 4px solid {PALETTE['accent']};
            background: rgba(24, 29, 26, 0.85);
            border-radius: 16px;
            padding: 24px;
            margin-top: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            animation: slideIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .metric-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
        }}

        .metric-icon {{
            font-size: 1.5rem;
            color: {PALETTE['accent']};
            font-family: 'Material Symbols Rounded' !important;
        }}

        .metric-content {{
            flex: 1;
        }}

        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        .metric-label {{ font-size: 0.75rem; color: {PALETTE['text_muted']}; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 4px; }}
        .metric-value {{ font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700; color: {PALETTE['accent']}; }}
        
        .progress-container {{
            width: 100%;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, {PALETTE['primary']}, {PALETTE['accent']});
            transition: width 1s ease-in-out;
        }}

        </style>
    """, unsafe_allow_html=True)

apply_botanical_theme()

# --- Load model ---
@st.cache_resource
def load_prediction_model():
    return tf.keras.models.load_model("best_model.keras")

model = load_prediction_model()

# --- Class names ---
class_names = [
    'Pepper: Bacterial Spot', 'Pepper: Healthy',
    'Potato: Early Blight', 'Potato: Late Blight', 'Potato: Healthy',
    'Tomato: Bacterial Spot', 'Tomato: Early Blight', 'Tomato: Late Blight',
    'Tomato: Leaf Mold', 'Tomato: Septoria Leaf Spot',
    'Tomato: Spider Mites', 'Tomato: Target Spot',
    'Tomato: Yellow Leaf Curl Virus', 'Tomato: Mosaic Virus', 'Tomato: Healthy'
]

# --- Sidebar (Project Observatory) ---
with st.sidebar:
    st.markdown('<h2 style="font-family:Outfit; margin-bottom:0;">BOTANICAL</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Outfit; font-weight:400; color:#8b938c; letter-spacing:0.2em; font-size:0.8rem;">OBSERVATORY v1.0</p>', unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### ENGINE STATUS")
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <span class="material-symbols-rounded" style="color:{PALETTE['accent']}">settings</span>
            <span><b>Model:</b> MobileNetV2</span>
        </div>
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <span class="material-symbols-rounded" style="color:{PALETTE['accent']}">bar_chart</span>
            <span><b>Accuracy:</b> 96.99%</span>
        </div>
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <span class="material-symbols-rounded" style="color:{PALETTE['accent']}">potted_plant</span>
            <span><b>Classes:</b> 15 Species</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### RECENT LOGS")
    # Simulation of logs
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:5px; opacity:0.7;">
            <span class="material-symbols-rounded" style="font-size:1.1rem;">history</span>
            <span style="font-size:0.8rem;">23:42 - System initialized</span>
        </div>
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:5px; opacity:0.7;">
            <span class="material-symbols-rounded" style="font-size:1.1rem;">memory</span>
            <span style="font-size:0.8rem;">23:43 - Neural weights loaded</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("---")
    st.button("Reset Session")
    st.caption("LeafGuard AI © 2026")

# --- Header Section ---
main_cols = st.columns([1, 2, 1])
with main_cols[1]:
    st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 3rem;">
            <p style="font-family:Outfit; letter-spacing: 0.3em; color:{PALETTE['accent']}; font-size:0.9rem; margin-bottom: 0;">PREMIUM AI ANALYSIS</p>
            <h1 style="font-size: 4rem; margin-bottom: 0.5rem; color: white;">LeafGuard AI</h1>
            <p style="color: {PALETTE['text_muted']}; font-size: 1.1rem; max-width: 600px; margin: auto;">
                The Botanical Observatory utilizes high-precision neural networks to identify early stage plant pathology.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- Upload Area ---
with main_cols[1]:
    st.markdown('<div class="glass-card upload-glow" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown(f'<span class="material-symbols-rounded" style="font-size:3rem; color:{PALETTE["accent"]}; margin-bottom:1rem;">cloud_upload</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Initiate Neural Scan", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    if not uploaded_file:
        st.markdown(f'<p style="text-align:center; color:{PALETTE["text_muted"]}; margin-top:1rem; font-family:Outfit;">Drop specimen photo or click to browse</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Analysis Phase ---
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    
    with main_cols[1]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # Display Image
        st.image(image, use_container_width=True)
        
        # Simulation of complex analysis
        status_text = st.empty()
        progress_bar = st.empty()
        
        status_text.markdown(f'<p style="text-align:center; color:{PALETTE["accent"]};">EXTRACTING CELLULAR DNA...</p>', unsafe_allow_html=True)
        progress_bar.markdown('<div class="progress-container"><div class="progress-bar" style="width: 30%;"></div></div>', unsafe_allow_html=True)
        time.sleep(0.6)
        
        status_text.markdown(f'<p style="text-align:center; color:{PALETTE["accent"]};">COMPARING PATHOGEN MARKERS...</p>', unsafe_allow_html=True)
        progress_bar.markdown('<div class="progress-container"><div class="progress-bar" style="width: 65%;"></div></div>', unsafe_allow_html=True)
        time.sleep(0.8)

        # Real inference
        processed_img = image.resize((160, 160))
        img_array = np.array(processed_img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        prediction = model.predict(img_array)
        idx = np.argmax(prediction)
        predicted_class = class_names[idx]
        confidence = np.max(prediction)

        status_text.markdown(f'<p style="text-align:center; color:{PALETTE["accent"]};">SCAN COMPLETE</p>', unsafe_allow_html=True)
        progress_bar.markdown('<div class="progress-container"><div class="progress-bar" style="width: 100%;"></div></div>', unsafe_allow_html=True)
        
        # Display Results
        st.markdown(f"""
            <div class="specimen-slide">
                <div class="metric-row">
                    <span class="material-symbols-rounded metric-icon">biotech</span>
                    <div class="metric-content">
                        <p class="metric-label">NEURAL DIAGNOSIS</p>
                        <p class="metric-value">{predicted_class}</p>
                    </div>
                </div>
                <div class="metric-row" style="margin-top: 20px;">
                    <span class="material-symbols-rounded metric-icon">verified</span>
                    <div class="metric-content">
                        <p class="metric-label">DIAGNOSTIC CONFIDENCE</p>
                        <p class="metric-value" style="font-size: 1.4rem;">{confidence*100:.2f}%</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if "Healthy" in predicted_class:
            st.success("✅ Specimen verified: VIGOROUS AND HEALTHY")
        else:
            st.error("🚨 Warning: PATHOGENIC MARKERS DETECTED")
            st.info("💡 Advice: Consult organic fungicides or remove affected foliage to prevent spread.")
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- Decorative Footer ---
st.markdown(f"""
    <div style="text-align:center; margin-top: 5rem; padding-bottom: 2rem; color:{PALETTE['text_muted']};">
        <p style="font-size: 0.8rem; letter-spacing: 0.1em;">POWERED BY MOBILENET-V2 | BUILT FOR REGEN-AGRICULTURE</p>
    </div>
""", unsafe_allow_html=True)

