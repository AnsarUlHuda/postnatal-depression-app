import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Postpartum Depression Screening",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== DESIGN SYSTEM =====================
INK = "#0F172A"
SLATE = "#475569"
MUTE = "#94A3B8"
LINE = "#E2E8F0"
SURFACE = "#FFFFFF"
PAGE_BG = "#F4F6FA"
ACCENT = "#4F46E5"
ACCENT_DARK = "#3730A3"
ACCENT_SOFT = "#EEF0FF"
DANGER = "#DC2626"
DANGER_SOFT = "#FEF2F2"
SUCCESS = "#059669"
SUCCESS_SOFT = "#ECFDF5"
WARN = "#D97706"
WARN_SOFT = "#FFFBEB"

st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.47.0/iconfont/tabler-icons.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {INK}; }}
.stApp {{ background: {PAGE_BG}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 1.5rem; max-width: 980px; }}

/* ---- Topbar ---- */
.topbar {{
    display: flex; align-items: center; justify-content: space-between;
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 14px;
    padding: 14px 22px; margin-bottom: 18px;
}}
.topbar-left {{ display: flex; align-items: center; gap: 12px; }}
.topbar-icon {{
    width: 40px; height: 40px; border-radius: 10px; background: {ACCENT_SOFT};
    display: flex; align-items: center; justify-content: center; color: {ACCENT}; font-size: 20px;
}}
.topbar-title {{ font-family: 'Manrope', sans-serif; font-weight: 700; font-size: 17px; margin: 0; color: {INK}; }}
.topbar-sub {{ font-size: 12.5px; color: {MUTE}; margin: 0; }}
.status-pill {{
    font-size: 12px; font-weight: 600; padding: 5px 12px; border-radius: 999px;
    background: {SUCCESS_SOFT}; color: {SUCCESS}; display: flex; align-items: center; gap: 6px;
}}
.status-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {SUCCESS}; display: inline-block; }}

/* ---- Step indicator ---- */
.steps {{ display: flex; gap: 10px; margin-bottom: 18px; }}
.step {{
    flex: 1; background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px;
    padding: 10px 14px; display: flex; align-items: center; gap: 10px;
}}
.step-num {{
    width: 22px; height: 22px; border-radius: 50%; background: {ACCENT}; color: white;
    font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.step-label {{ font-size: 12.5px; font-weight: 600; color: {INK}; }}
.step-desc {{ font-size: 11px; color: {MUTE}; }}

/* ---- Section cards ---- */
.section-card {{
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 14px;
    padding: 22px 24px; margin-bottom: 16px;
}}
.section-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }}
.section-head i {{ color: {ACCENT}; font-size: 16px; }}
.section-title {{
    font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {ACCENT_DARK};
}}

/* ---- Form controls ---- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
    color: {SLATE} !important; font-size: 13.5px !important; font-weight: 500 !important;
}}
.stSelectbox div[data-baseweb="select"] > div {{
    border-radius: 9px !important; border-color: {LINE} !important; background: #FAFBFD !important;
}}
.stSelectbox div[data-baseweb="select"] * {{ color: {INK} !important; font-size: 13.5px !important; }}

/* ---- Primary button ---- */
.stButton > button[kind="primary"] {{
    background: {ACCENT} !important; color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.7rem 2rem !important; font-weight: 600 !important;
    font-size: 14.5px !important; box-shadow: none !important; transition: background 0.15s ease !important;
}}
.stButton > button[kind="primary"]:hover {{ background: {ACCENT_DARK} !important; }}

.stDownloadButton > button {{
    background: {SURFACE} !important; color: {ACCENT} !important; border: 1.5px solid {ACCENT} !important;
    border-radius: 10px !important; font-weight: 600 !important; font-size: 13.5px !important;
}}
.stDownloadButton > button:hover {{ background: {ACCENT_SOFT} !important; }}

/* ---- Result banner ---- */
.result-banner {{
    display: flex; align-items: center; gap: 16px; border-radius: 14px; padding: 18px 22px; margin-bottom: 16px;
}}
.result-banner.high {{ background: {DANGER_SOFT}; border: 1px solid #FCA5A5; }}
.result-banner.low {{ background: {SUCCESS_SOFT}; border: 1px solid #6EE7B7; }}
.result-icon {{
    width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0;
}}
.result-icon.high {{ background: #FEE2E2; color: {DANGER}; }}
.result-icon.low {{ background: #D1FAE5; color: {SUCCESS}; }}
.result-title {{ font-family: 'Manrope', sans-serif; font-weight: 700; font-size: 17px; margin: 0; }}
.result-title.high {{ color: {DANGER}; }}
.result-title.low {{ color: {SUCCESS}; }}
.result-sub {{ font-size: 13px; color: {SLATE}; margin: 2px 0 0 0; }}

/* ---- Metric cards ---- */
.metric-card {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 12px; padding: 14px 16px; }}
.metric-label {{ font-size: 11.5px; color: {MUTE}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 4px 0; }}
.metric-value {{ font-size: 22px; font-weight: 700; color: {INK}; margin: 0; font-family: 'Manrope', sans-serif; }}

/* ---- Recommendations ---- */
.rec-item {{
    display: flex; align-items: flex-start; gap: 10px; padding: 9px 0; border-bottom: 1px solid {LINE};
}}
.rec-item:last-child {{ border-bottom: none; }}
.rec-item i {{ color: {ACCENT}; font-size: 15px; margin-top: 2px; flex-shrink: 0; }}
.rec-item p {{ margin: 0; font-size: 13.5px; color: {SLATE}; }}

/* ---- Disclaimer ---- */
.disclaimer {{
    display: flex; align-items: center; gap: 10px; background: {WARN_SOFT}; border: 1px solid #FDE68A;
    border-radius: 10px; padding: 10px 16px; margin-top: 18px; font-size: 12.5px; color: #92400E;
}}
.disclaimer i {{ color: {WARN}; font-size: 16px; flex-shrink: 0; }}

hr {{ border-color: {LINE} !important; margin: 1.25rem 0 !important; }}
</style>
""", unsafe_allow_html=True)

# ===================== ENCODING MAPS =====================
# These exactly replicate the notebook's training mappings
AGE_MAP = {"25-30": 27.5, "30-35": 32.5, "35-40": 37.5, "40-45": 42.5, "45-50": 47.5}
SYMPTOM_MAP_3 = {"No": 0, "Sometimes": 1, "Yes": 2}
SLEEP_MAP = {"No": 0, "Two or more days a week": 1, "Yes": 2}
OVEREAT_MAP = {"No": 0, "Not at all": 0, "Yes": 2}
ANXIOUS_MAP = {"No": 0, "Yes": 2}
GUILT_MAP = {"No": 0, "Maybe": 1, "Yes": 2}
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
    st.error("Model file 'depression_model.pkl' not found. Place it in the same folder as this app.")
    st.stop()

# ===================== PDF GENERATOR =====================
def generate_pdf(age_group, prediction_text, risk_prob, recommendations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle('Title',   parent=styles['Title'],
                                  textColor=colors.HexColor('#3730A3'), fontSize=18, spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                   textColor=colors.HexColor('#374151'), fontSize=13, spaceAfter=4)
    body_style   = ParagraphStyle('Body',    parent=styles['BodyText'],
                                  textColor=colors.HexColor('#374151'), fontSize=11, leading=16)
    disc_style   = ParagraphStyle('Disc',    parent=styles['BodyText'],
                                  textColor=colors.HexColor('#92400e'), fontSize=9)
    content = []
    content.append(Paragraph("Postpartum Depression Prediction Report", title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#c7d2fe'), spaceAfter=12))
    content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", body_style))
    content.append(Paragraph(f"<b>Age Group:</b> {age_group}", body_style))
    content.append(Paragraph(f"<b>Prediction:</b> {prediction_text}", body_style))
    content.append(Paragraph(f"<b>Risk Probability:</b> {risk_prob:.2f}%", body_style))
    content.append(Spacer(1, 16))
    content.append(Paragraph("Recommendations", heading_style))
    content.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e0e7ff'), spaceAfter=8))
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

# ===================== GAUGE CHART =====================
def render_gauge(risk_prob):
    color = DANGER if risk_prob >= 50 else SUCCESS
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_prob,
        number={'suffix': "%", 'font': {'size': 32, 'color': INK, 'family': 'Manrope'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': LINE, 'tickfont': {'size': 10, 'color': MUTE}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': "white",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#ECFDF5'},
                {'range': [40, 70], 'color': '#FFFBEB'},
                {'range': [70, 100], 'color': '#FEF2F2'},
            ],
            'threshold': {'line': {'color': INK, 'width': 2}, 'thickness': 0.75, 'value': 50}
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", font={'family': 'Inter'})
    return fig

# ===================== TOPBAR =====================
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-icon"><i class="ti ti-stethoscope"></i></div>
        <div>
            <p class="topbar-title">Postpartum Depression Screening</p>
            <p class="topbar-sub">Clinical decision support tool</p>
        </div>
    </div>
    <span class="status-pill"><span class="status-dot"></span>Model active</span>
</div>
""", unsafe_allow_html=True)

# ===================== STEP INDICATOR =====================
st.markdown("""
<div class="steps">
    <div class="step"><div class="step-num">1</div><div><div class="step-label">Patient info</div><div class="step-desc">Age group</div></div></div>
    <div class="step"><div class="step-num">2</div><div><div class="step-label">Symptom review</div><div class="step-desc">Emotional and physical</div></div></div>
    <div class="step"><div class="step-num">3</div><div><div class="step-label">Result</div><div class="step-desc">Risk score and report</div></div></div>
</div>
""", unsafe_allow_html=True)

# ===================== FORM: PATIENT INFO =====================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-head"><i class="ti ti-user"></i><span class="section-title">Patient information</span></div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1.4])
with col1:
    Age = st.selectbox("Age group", ["25-30", "30-35", "35-40", "40-45", "45-50"])
with col2:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.caption("Select the patient's age range at time of screening")
st.markdown('</div>', unsafe_allow_html=True)

# ===================== FORM: EMOTIONAL SYMPTOMS =====================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-head"><i class="ti ti-mood-sad"></i><span class="section-title">Emotional and mood symptoms</span></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    Feeling_sad = st.selectbox("Feeling sad or tearful", ["No", "Sometimes", "Yes"])
    Irritable = st.selectbox("Irritable towards baby and partner", ["No", "Sometimes", "Yes"])
    Feeling_guilt = st.selectbox("Feeling of guilt", ["No", "Maybe", "Yes"])
with col2:
    Feeling_anxious = st.selectbox("Feeling anxious", ["No", "Yes"])
    Problems_concentrating = st.selectbox("Problems concentrating or making decisions", ["No", "Often", "Yes"])
    Bonding_issues = st.selectbox("Problems bonding with baby", ["No", "Sometimes", "Yes"])
st.markdown('</div>', unsafe_allow_html=True)

# ===================== FORM: PHYSICAL SYMPTOMS =====================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-head"><i class="ti ti-activity"></i><span class="section-title">Physical symptoms</span></div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    Trouble_sleeping = st.selectbox("Trouble sleeping at night", ["No", "Two or more days a week", "Yes"])
with col2:
    Overeating = st.selectbox("Overeating or loss of appetite", ["No", "Not at all", "Yes"])
st.markdown('</div>', unsafe_allow_html=True)

# ===================== ENCODE INPUT =====================
encoded = {
    "Age":                                        AGE_MAP[Age],
    "Feeling sad or Tearful":                     SYMPTOM_MAP_3[Feeling_sad],
    "Irritable towards baby & partner":           SYMPTOM_MAP_3[Irritable],
    "Trouble sleeping at night":                  SLEEP_MAP[Trouble_sleeping],
    "Problems concentrating or making decision":  CONC_MAP[Problems_concentrating],
    "Overeating or loss of appetite":             OVEREAT_MAP[Overeating],
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
_, btn_col, _ = st.columns([1, 1.4, 1])
with btn_col:
    run = st.button("Analyse depression risk", use_container_width=True, type="primary")

if run:
    try:
        probability = model.predict_proba(input_array)
        risk_score  = probability[0][1]
        prediction = 1 if risk_score >= 0.50 else 0
        risk_prob = round(risk_score * 100, 2)

        if prediction == 1:
            prediction_text = "High Risk of Postpartum Depression"
            recommendations = (
                "Consult a mental health professional immediately.\n"
                "Schedule a formal clinical evaluation.\n"
                "Ensure strong emotional and family support.\n"
                "Monitor and document symptoms daily."
            )
            st.markdown(f"""
            <div class="result-banner high">
                <div class="result-icon high"><i class="ti ti-alert-triangle"></i></div>
                <div><p class="result-title high">High risk detected</p><p class="result-sub">Immediate clinical attention recommended</p></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            prediction_text = "Low Risk of Postpartum Depression"
            recommendations = (
                "Continue routine postpartum monitoring.\n"
                "Maintain healthy sleep and nutrition habits.\n"
                "Attend regular health checkups.\n"
                "Seek professional support if new symptoms arise."
            )
            st.markdown(f"""
            <div class="result-banner low">
                <div class="result-icon low"><i class="ti ti-circle-check"></i></div>
                <div><p class="result-title low">Low risk</p><p class="result-sub">Continue routine postpartum monitoring</p></div>
            </div>
            """, unsafe_allow_html=True)

        gcol, mcol = st.columns([1.3, 1])
        with gcol:
            st.plotly_chart(render_gauge(risk_prob), use_container_width=True, config={'displayModeBar': False})
        with mcol:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:10px">
                <p class="metric-label">Risk probability</p>
                <p class="metric-value">{risk_prob}%</p>
            </div>
            <div class="metric-card">
                <p class="metric-label">Decision threshold</p>
                <p class="metric-value">50%</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-head"><i class="ti ti-clipboard-check"></i><span class="section-title">Recommendations</span></div>', unsafe_allow_html=True)
        for line in recommendations.strip().split('\n'):
            st.markdown(f'<div class="rec-item"><i class="ti ti-point-filled"></i><p>{line.strip()}</p></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        pdf_file = generate_pdf(Age, prediction_text, risk_prob, recommendations)
        st.download_button(
            label="Download full PDF report",
            data=pdf_file,
            file_name="postpartum_depression_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ===================== DISCLAIMER =====================
st.markdown("""
<div class="disclaimer">
    <i class="ti ti-info-circle"></i>
    <span><strong>Medical disclaimer:</strong> This tool is intended for screening purposes only and does not replace a clinical diagnosis or the judgement of a qualified healthcare professional.</span>
</div>
""", unsafe_allow_html=True)
