import streamlit as st
import pandas as pd
import numpy as np
import joblib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Postpartum Depression Prediction",
    page_icon="🩺",
    layout="centered"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #f0fff4 100%);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

/* Force readable label/text colors regardless of workspace theme (light/dark) */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCaptionContainer"] p,
.stSelectbox div[data-baseweb="select"] * {
    color: #1e1b4b !important;
}
.form-card p, .form-card label {
    color: #1e1b4b !important;
}

.hero-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 20px 60px rgba(102,126,234,0.35);
}
.hero-card h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #ffffff;
    margin: 0.5rem 0 0.3rem 0;
    line-height: 1.2;
}
.hero-card p {
    color: rgba(255,255,255,0.85);
    font-size: 0.95rem;
    margin: 0;
    font-weight: 300;
}
.hero-icon { font-size: 3rem; margin-bottom: 0.5rem; display: block; }

.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.75rem;
    margin-top: 0.25rem;
}

.form-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.75rem 1.75rem 1.25rem 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border: 1px solid rgba(124,58,237,0.08);
}

.result-high {
    background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
    border: 2px solid #f87171;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.result-low {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 2px solid #4ade80;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.result-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0.25rem 0;
}
.result-high .result-title { color: #dc2626; }
.result-low .result-title  { color: #16a34a; }

.risk-badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.5rem;
}
.badge-high { background: #fee2e2; color: #b91c1c; }
.badge-low  { background: #d1fae5; color: #065f46; }

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    border-radius: 999px !important;
}
.stProgress > div > div > div {
    background: #e9d5ff !important;
    border-radius: 999px !important;
}

[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #ede9fe;
}
[data-testid="metric-container"] label {
    color: #7c3aed !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1e1b4b !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 8px 24px rgba(102,126,234,0.4) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(102,126,234,0.5) !important;
}

.stDownloadButton > button {
    background: #ffffff !important;
    color: #7c3aed !important;
    border: 2px solid #7c3aed !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: #7c3aed !important;
    color: #ffffff !important;
}

.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: #ddd6fe !important;
    background: #faf5ff !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}

.rec-box {
    background: #faf5ff;
    border-left: 4px solid #7c3aed;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
}
.rec-box p { margin: 0.3rem 0; color: #374151; font-size: 0.9rem; }

.disclaimer {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-top: 1.5rem;
    font-size: 0.8rem;
    color: #92400e;
    text-align: center;
}

.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #c4b5fd, transparent);
    margin: 1.5rem 0;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ===================== ENCODING MAPS =====================
# These exactly replicate the notebook's training mappings

AGE_MAP = {
    "25-30": 27.5,
    "30-35": 32.5,
    "35-40": 37.5,
    "40-45": 42.5,
    "45-50": 47.5
}

# Notebook: No=0, Sometimes=1, Yes=2
SYMPTOM_MAP_3 = {"No": 0, "Sometimes": 1, "Yes": 2}

# Notebook: No=0, Two or more days a week=1, Yes=2
SLEEP_MAP = {"No": 0, "Two or more days a week": 1, "Yes": 2}

# Notebook: Not at all=0, No=0, Yes=2
OVEREAT_MAP = {"No": 0, "Not at all": 0, "Yes": 2}

# Notebook: No=0, Yes=2
ANXIOUS_MAP = {"No": 0, "Yes": 2}

# Notebook: No=0, Maybe=1, Yes=2
GUILT_MAP = {"No": 0, "Maybe": 1, "Yes": 2}

# Notebook: No=0, Often=1, Yes=2
CONC_MAP = {"No": 0, "Often": 1, "Yes": 2}

# ===================== LOAD MODEL =====================
@st.cache_resource
def load_model():
    model = joblib.load("depression_model.pkl")
    try:
        scaler = joblib.load("depression_scaler.pkl")
    except FileNotFoundError:
        scaler = None
    return model, scaler

try:
    model, scaler = load_model()
except FileNotFoundError:
    st.error("❌ Model file 'depression_model.pkl' not found. Place it in the same folder as this app.")
    st.stop()

# ===================== PDF GENERATOR =====================
def generate_pdf(age_group, prediction_text, risk_prob, recommendations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle('Title',   parent=styles['Title'],
                                  textColor=colors.HexColor('#5b21b6'), fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                   textColor=colors.HexColor('#374151'), fontSize=13, spaceAfter=4)
    body_style   = ParagraphStyle('Body',    parent=styles['BodyText'],
                                  textColor=colors.HexColor('#374151'), fontSize=11, leading=16)
    disc_style   = ParagraphStyle('Disc',    parent=styles['BodyText'],
                                  textColor=colors.HexColor('#92400e'), fontSize=9)
    content = []
    content.append(Paragraph("Postpartum Depression Prediction Report", title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c4b5fd'), spaceAfter=12))
    content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", body_style))
    content.append(Paragraph(f"<b>Age Group:</b> {age_group}", body_style))
    content.append(Paragraph(f"<b>Prediction:</b> {prediction_text}", body_style))
    content.append(Paragraph(f"<b>Risk Probability:</b> {risk_prob:.2f}%", body_style))
    content.append(Spacer(1, 16))
    content.append(Paragraph("Recommendations", heading_style))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e9d5ff'), spaceAfter=8))
    for line in recommendations.strip().split('\n'):
        line = line.strip()
        if line:
            content.append(Paragraph(f"- {line.lstrip('- ')}", body_style))
    content.append(Spacer(1, 16))
    content.append(Paragraph(
        "<i>This report is for screening purposes only and does not replace clinical diagnosis.</i>",
        disc_style))
    doc.build(content)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ===================== HERO =====================
st.markdown("""
<div class="hero-card">
    <span class="hero-icon">🩺</span>
    <h1>Postnatal Depression Prediction</h1>
    <p>Clinical screening tool</p>
</div>
""", unsafe_allow_html=True)

# ===================== FORM =====================
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">Patient Information</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    Age = st.selectbox("👤 Age Group", ["25-30", "30-35", "35-40", "40-45", "45-50"])
with col2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.caption("Select the patient's age range")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">Emotional & Mood Symptoms</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    Feeling_sad          = st.selectbox("😢 Feeling Sad or Tearful",                    ["No", "Sometimes", "Yes"])
    Irritable            = st.selectbox("😠 Irritable Towards Baby & Partner",           ["No", "Sometimes", "Yes"])
    Feeling_guilt        = st.selectbox("😔 Feeling of Guilt",                           ["No", "Maybe", "Yes"])
with col2:
    Feeling_anxious      = st.selectbox("😰 Feeling Anxious",                            ["No", "Yes"])
    Problems_concentrating = st.selectbox("🧠 Problems Concentrating / Making Decisions",["No", "Often", "Yes"])
    Bonding_issues       = st.selectbox("👶 Problems Bonding with Baby",                 ["No", "Sometimes", "Yes"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<p class="section-label">Physical Symptoms</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    Trouble_sleeping = st.selectbox("🌙 Trouble Sleeping at Night",
                                    ["No", "Two or more days a week", "Yes"])
with col2:
    Overeating = st.selectbox("🍽️ Overeating or Loss of Appetite",
                              ["No", "Not at all", "Yes"])
st.markdown('</div>', unsafe_allow_html=True)

# ===================== ENCODE INPUT =====================
encoded = {
    "Age":                                        AGE_MAP[Age],
    "Feeling sad or Tearful":                     SYMPTOM_MAP_3[Feeling_sad],
    "Irritable towards baby & partner":           SYMPTOM_MAP_3[Irritable],
    "Trouble sleeping at night":                  SLEEP_MAP[Trouble_sleeping],
    "Problems concentrating or making decision":  CONC_MAP[Problems_concentrating],
    "Overeating or loss of appetite":             OVEREAT_MAP[Overeating],   # FIX: max=1 not 2
    "Feeling anxious":                            ANXIOUS_MAP[Feeling_anxious],
    "Feeling of guilt":                           GUILT_MAP[Feeling_guilt],
    "Problems of bonding with baby":              SYMPTOM_MAP_3[Bonding_issues],
}

input_df = pd.DataFrame([encoded])
if scaler is not None:
    input_array = scaler.transform(input_df)
else:
    input_array = input_df.values

# ===================== PREDICT =====================
st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

if st.button("🔍  Analyse Depression Risk", use_container_width=True, type="primary"):
    try:
        probability = model.predict_proba(input_array)
        risk_score  = probability[0][1]

        # FIX: threshold lowered from 0.65 → 0.50 (standard classifier default)
        # The model was trained on balanced data (SMOTE), so 0.50 is correct
        prediction = 1 if risk_score >= 0.50 else 0

        risk_prob = round(risk_score * 100, 2)

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Prediction Result</p>', unsafe_allow_html=True)

        if prediction == 1:
            prediction_text = "High Risk of Postnatal Depression"
            recommendations = (
                "Consult a mental health professional immediately.\n"
                "Schedule a formal clinical evaluation.\n"
                "Ensure strong emotional and family support.\n"
                "Monitor and document symptoms daily."
            )
            st.markdown("""
            <div class="result-high">
                <div style="font-size:2.5rem">⚠️</div>
                <div class="result-title">High Risk Detected</div>
                <span class="risk-badge badge-high">Immediate clinical attention recommended</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            prediction_text = "Low Risk of Postnatal Depression"
            recommendations = (
                "Continue routine postnatal monitoring.\n"
                "Maintain healthy sleep and nutrition habits.\n"
                "Attend regular health checkups.\n"
                "Seek professional support if new symptoms arise."
            )
            st.markdown("""
            <div class="result-low">
                <div style="font-size:2.5rem">✅</div>
                <div class="result-title">Low Risk</div>
                <span class="risk-badge badge-low">Continue routine monitoring</span>
            </div>
            """, unsafe_allow_html=True)

        # Metric + progress bar
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Depression Risk Probability", f"{risk_prob}%")
        with col2:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.progress(min(risk_score, 1.0))
            if risk_prob >= 70:
                st.markdown("🔴 **Immediate** evaluation strongly advised.")
            elif risk_prob >= 40:
                st.markdown("🟡 **Moderate** risk — schedule a follow-up assessment.")
            else:
                st.markdown("🟢 **Low** risk — routine postnatal monitoring is sufficient.")

        # Recommendations
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Recommendations</p>', unsafe_allow_html=True)
        st.markdown('<div class="rec-box">', unsafe_allow_html=True)
        for line in recommendations.strip().split('\n'):
            st.markdown(f"<p>▸ {line.strip()}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # PDF download
        pdf_file = generate_pdf(Age, prediction_text, risk_prob, recommendations)
        st.download_button(
            label="📄  Download Full PDF Report",
            data=pdf_file,
            file_name="postnatal_depression_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ===================== DISCLAIMER =====================
st.markdown("""
<div class="disclaimer">
    ⚕️ <strong>Medical Disclaimer:</strong> This tool is intended for screening purposes only
    and does not replace a clinical diagnosis or the judgement of a qualified healthcare professional.
</div>
""", unsafe_allow_html=True)
