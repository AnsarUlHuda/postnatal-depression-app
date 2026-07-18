import base64
from datetime import datetime
from io import BytesIO
from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


# ===================== PAGE CONFIG =====================
# NOTE: page_icon must be a single emoji character, an emoji shortcode
# (e.g. ":stethoscope:"), "random", a Material icon, or an image path/URL.
# A plain string like "PND" is none of these and raises an exception on load.
st.set_page_config(
    page_title="Postpartum Depression Screening",
    page_icon="🤱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===================== DESIGN TOKENS =====================
INK = "#15233A"
SLATE = "#607089"
MUTE = "#8EA0B8"
LINE = "#DCE6F2"
SURFACE = "#FFFFFF"
PAGE_BG = "#F6F9FC"
SOFT = "#EEF7F7"
TEAL = "#0F766E"
TEAL_DARK = "#115E59"
TEAL_SOFT = "#E4F7F5"
CORAL = "#E56A5F"
CORAL_SOFT = "#FFF0ED"
INDIGO = "#334E9B"
INDIGO_SOFT = "#EEF2FF"
GOLD = "#C88A1D"
GOLD_SOFT = "#FFF8E8"
DANGER = "#C2413A"
DANGER_SOFT = "#FFF1F0"
SUCCESS = "#138A63"
SUCCESS_SOFT = "#ECFDF5"
ASSET_DIR = Path(__file__).parent / "assets"
HERO_IMAGE = ASSET_DIR / "maternal-dashboard-hero.png"


st.markdown(
    f"""
<style>
html, body, [class*="css"] {{
    font-family: "Segoe UI", Inter, Arial, sans-serif;
    color: {INK};
}}
.stApp {{
    background:
        radial-gradient(circle at 14% 4%, rgba(15, 118, 110, 0.13), transparent 28rem),
        linear-gradient(180deg, #F8FBFD 0%, {PAGE_BG} 42%, #F4F7FB 100%);
}}
#MainMenu, footer, [data-testid="stHeader"] {{ visibility: hidden; }}
.block-container {{
    max-width: 1220px;
    padding: 1.35rem 2.2rem 2.75rem;
}}
div[data-testid="stVerticalBlock"] {{ gap: 1rem; }}
.app-shell {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}}
.brand {{
    display: flex;
    align-items: center;
    gap: .8rem;
}}
.brand-mark {{
    width: 42px;
    height: 42px;
    border-radius: 11px;
    background: linear-gradient(135deg, {TEAL}, {INDIGO});
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    letter-spacing: 0;
    box-shadow: 0 12px 26px rgba(15, 118, 110, .22);
}}
.brand-title {{
    margin: 0;
    font-size: 1rem;
    font-weight: 800;
    color: {INK};
}}
.brand-subtitle {{
    margin: .12rem 0 0;
    color: {MUTE};
    font-size: .78rem;
    font-weight: 600;
}}
.status-bar {{
    display: flex;
    align-items: center;
    gap: .55rem;
    padding: .55rem .8rem;
    border: 1px solid {LINE};
    border-radius: 999px;
    background: rgba(255,255,255,.8);
    color: {TEAL_DARK};
    font-size: .78rem;
    font-weight: 800;
}}
.status-dot {{
    width: .48rem;
    height: .48rem;
    border-radius: 99px;
    background: {SUCCESS};
    box-shadow: 0 0 0 5px rgba(19, 138, 99, .12);
}}
.hero {{
    display: grid;
    grid-template-columns: minmax(0, .96fr) minmax(320px, .74fr);
    align-items: stretch;
    overflow: hidden;
    min-height: 330px;
    border: 1px solid {LINE};
    border-radius: 8px;
    background: {SURFACE};
    box-shadow: 0 22px 70px rgba(21, 35, 58, .08);
    margin-bottom: 1rem;
}}
.hero-copy {{
    padding: 2rem 2.15rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.hero-copy h1 {{
    margin: 0;
    max-width: 720px;
    font-size: clamp(2.05rem, 4vw, 4rem);
    line-height: 1.02;
    letter-spacing: 0;
    font-weight: 850;
    color: {INK};
}}
.hero-copy p {{
    margin: 1rem 0 0;
    max-width: 620px;
    font-size: 1.02rem;
    line-height: 1.7;
    color: {SLATE};
}}
.hero-actions {{
    display: flex;
    align-items: center;
    gap: .8rem;
    margin-top: 1.45rem;
    flex-wrap: wrap;
}}
.hero-chip {{
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    min-height: 34px;
    padding: .45rem .7rem;
    border-radius: 8px;
    border: 1px solid {LINE};
    background: #FBFDFE;
    color: {SLATE};
    font-size: .76rem;
    font-weight: 800;
}}
.chip-mark {{
    width: .48rem;
    height: .48rem;
    border-radius: 99px;
    background: {CORAL};
}}
.hero-image {{
    min-height: 100%;
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, {TEAL_SOFT}, {INDIGO_SOFT});
}}
.hero-image::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(255,255,255,.92), rgba(255,255,255,.18) 28%, transparent 48%);
    z-index: 2;
    pointer-events: none;
}}
.hero-image img {{
    width: 100%;
    height: 100%;
    min-height: 330px;
    object-fit: cover;
    display: block;
}}
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: .85rem;
    margin-bottom: 1rem;
}}
.stat-card {{
    background: rgba(255,255,255,.86);
    border: 1px solid {LINE};
    border-radius: 8px;
    padding: 1rem 1.05rem;
    min-height: 112px;
}}
.stat-label {{
    margin: 0 0 .5rem;
    color: {MUTE};
    font-size: .72rem;
    text-transform: uppercase;
    letter-spacing: .04em;
    font-weight: 850;
}}
.stat-value {{
    margin: 0;
    color: {INK};
    font-size: 1.55rem;
    line-height: 1;
    font-weight: 850;
}}
.stat-note {{
    margin: .45rem 0 0;
    color: {SLATE};
    font-size: .78rem;
    line-height: 1.45;
}}
.dashboard-grid {{
    display: grid;
    grid-template-columns: minmax(0, .98fr) minmax(340px, .72fr);
    gap: 1rem;
    align-items: start;
}}
.panel {{
    background: rgba(255,255,255,.92);
    border: 1px solid {LINE};
    border-radius: 8px;
    padding: 1.2rem;
    box-shadow: 0 14px 38px rgba(21, 35, 58, .05);
}}
.panel-title {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
}}
.panel-title h2 {{
    margin: 0;
    color: {INK};
    font-size: 1.05rem;
    line-height: 1.25;
    font-weight: 850;
}}
.panel-title span {{
    color: {MUTE};
    font-size: .75rem;
    font-weight: 800;
}}
.section-rule {{
    height: 1px;
    background: {LINE};
    margin: 1rem 0;
}}
.helper-copy {{
    margin: -.35rem 0 1rem;
    color: {SLATE};
    line-height: 1.55;
    font-size: .86rem;
}}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
    color: {INK} !important;
    font-size: .86rem !important;
    font-weight: 750 !important;
}}
.stSelectbox div[data-baseweb="select"] > div {{
    min-height: 44px;
    border-radius: 8px !important;
    border-color: {LINE} !important;
    background: #FAFCFE !important;
    box-shadow: none !important;
}}
.stSelectbox div[data-baseweb="select"] * {{
    color: {INK} !important;
    font-size: .88rem !important;
}}
.stButton > button[kind="primary"] {{
    min-height: 48px;
    background: linear-gradient(135deg, {TEAL}, {INDIGO}) !important;
    color: white !important;
    border: 0 !important;
    border-radius: 8px !important;
    font-size: .92rem !important;
    font-weight: 850 !important;
    box-shadow: 0 14px 24px rgba(15, 118, 110, .22) !important;
}}
.stButton > button[kind="primary"]:hover {{
    filter: brightness(.96);
}}
.stDownloadButton > button {{
    min-height: 46px;
    background: #FFFFFF !important;
    color: {TEAL_DARK} !important;
    border: 1px solid {TEAL} !important;
    border-radius: 8px !important;
    font-weight: 850 !important;
}}
.result-card {{
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid {LINE};
    margin-bottom: 1rem;
}}
.result-card.high {{
    background: linear-gradient(135deg, {DANGER_SOFT}, #FFFFFF);
    border-color: #F3B7B2;
}}
.result-card.low {{
    background: linear-gradient(135deg, {SUCCESS_SOFT}, #FFFFFF);
    border-color: #B7E4D2;
}}
.result-title {{
    margin: 0;
    font-size: 1.25rem;
    font-weight: 850;
}}
.result-title.high {{ color: {DANGER}; }}
.result-title.low {{ color: {SUCCESS}; }}
.result-sub {{
    margin: .35rem 0 0;
    color: {SLATE};
    font-size: .9rem;
    line-height: 1.55;
}}
.rec-item {{
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: .7rem;
    align-items: start;
    padding: .78rem 0;
    border-bottom: 1px solid {LINE};
}}
.rec-item:last-child {{ border-bottom: 0; }}
.rec-num {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: {TEAL_SOFT};
    color: {TEAL_DARK};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: .78rem;
    font-weight: 900;
}}
.rec-item p {{
    margin: 0;
    color: {SLATE};
    font-size: .9rem;
    line-height: 1.55;
}}
.info-strip {{
    display: grid;
    grid-template-columns: 42px 1fr;
    gap: .8rem;
    align-items: start;
    background: {GOLD_SOFT};
    border: 1px solid #F2D18B;
    border-radius: 8px;
    padding: .9rem 1rem;
    margin-top: 1rem;
}}
.info-icon {{
    width: 42px;
    height: 42px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #FFFFFF;
    color: {GOLD};
    font-weight: 900;
}}
.info-strip p {{
    margin: 0;
    color: #805A16;
    font-size: .84rem;
    line-height: 1.55;
}}
.mini-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: .84rem;
}}
.mini-table td {{
    padding: .65rem 0;
    border-bottom: 1px solid {LINE};
    color: {SLATE};
}}
.mini-table td:last-child {{
    text-align: right;
    color: {INK};
    font-weight: 850;
}}
.scale-row {{
    display: grid;
    grid-template-columns: 72px 1fr 44px;
    align-items: center;
    gap: .65rem;
    margin: .68rem 0;
    color: {SLATE};
    font-size: .82rem;
}}
.scale-bar {{
    height: 9px;
    border-radius: 99px;
    background: #EDF2F7;
    overflow: hidden;
}}
.scale-fill {{
    height: 100%;
    border-radius: inherit;
    background: linear-gradient(90deg, {TEAL}, {CORAL});
}}
@media (max-width: 900px) {{
    .block-container {{ padding: 1rem; }}
    .hero, .dashboard-grid {{ grid-template-columns: 1fr; }}
    .hero {{ min-height: auto; }}
    .hero-image {{ min-height: 230px; order: -1; }}
    .hero-image img {{ min-height: 230px; }}
    .stats-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .app-shell {{ align-items: flex-start; flex-direction: column; }}
}}
@media (max-width: 560px) {{
    .stats-grid {{ grid-template-columns: 1fr; }}
    .hero-copy {{ padding: 1.3rem; }}
    .hero-copy h1 {{ font-size: 2.1rem; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# ===================== ENCODING MAPS =====================
AGE_MAP = {"25-30": 27.5, "30-35": 32.5, "35-40": 37.5, "40-45": 42.5, "45-50": 47.5}
SYMPTOM_MAP_3 = {"No": 0, "Sometimes": 1, "Yes": 2}
SLEEP_MAP = {"No": 0, "Two or more days a week": 1, "Yes": 2}
# Fixed: previously "No" and "Not at all" both mapped to 0, so this field
# could never register a "Watch" (mid-severity) state. Now a genuine 3-level
# scale, consistent with the other symptom fields.
OVEREAT_MAP = {"No": 0, "Sometimes": 1, "Yes": 2}
ANXIOUS_MAP = {"No": 0, "Yes": 2}
GUILT_MAP = {"No": 0, "Maybe": 1, "Yes": 2}
CONC_MAP = {"No": 0, "Often": 1, "Yes": 2}
SYMPTOM_LABELS = {
    "Feeling sad or Tearful": "Sadness",
    "Irritable towards baby & partner": "Irritability",
    "Trouble sleeping at night": "Sleep",
    "Problems concentrating or making decision": "Concentration",
    "Overeating or loss of appetite": "Appetite",
    "Feeling anxious": "Anxiety",
    "Feeling of guilt": "Guilt",
    "Problems of bonding with baby": "Bonding",
}
FEATURE_ORDER = list(SYMPTOM_LABELS.keys())


# ===================== LOAD MODEL =====================
@st.cache_resource(show_spinner=False)
def load_model():
    """Load the model and (optional) scaler.

    Returns (model, scaler, error_message). error_message is None on success,
    so callers can distinguish "no scaler saved" (fine) from "model missing
    or unreadable" (fatal) without the whole app crashing on import.
    """
    try:
        model = joblib.load("depression_model.pkl")
    except FileNotFoundError:
        return None, None, "Model file 'depression_model.pkl' was not found in this folder."
    except Exception as exc:  # corrupted file, version mismatch, etc.
        return None, None, f"The model file could not be loaded: {exc}"

    scaler = None
    try:
        scaler = joblib.load("depression_scaler.pkl")
    except FileNotFoundError:
        scaler = None  # scaler is optional
    except Exception as exc:
        return model, None, f"The model loaded, but the scaler file could not be read: {exc}"

    return model, scaler, None


model, scaler, load_error = load_model()
if load_error:
    st.error(load_error)
    st.stop()

if not hasattr(model, "predict_proba"):
    st.error(
        "The loaded model does not expose predict_proba, so a risk probability "
        "cannot be computed. Please provide a classifier that supports it."
    )
    st.stop()


# ===================== HELPERS =====================
def image_to_base64(path: Path):
    """Read an image file and return a base64 string, or None if unreadable."""
    try:
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        return None


def generate_pdf(age_group, prediction_text, risk_prob, recommendations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=colors.HexColor(TEAL_DARK),
        fontSize=18,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=colors.HexColor(INK),
        fontSize=13,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#374151"),
        fontSize=11,
        leading=16,
    )
    disc_style = ParagraphStyle(
        "Disc",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#805A16"),
        fontSize=9,
    )
    content = [
        Paragraph("Postpartum Depression Screening Report", title_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#A7DCD7"), spaceAfter=12),
        Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", body_style),
        Paragraph(f"<b>Age Group:</b> {age_group}", body_style),
        Paragraph(f"<b>Prediction:</b> {prediction_text}", body_style),
        Paragraph(f"<b>Risk Probability:</b> {risk_prob:.2f}%", body_style),
        Spacer(1, 16),
        Paragraph("Recommended next steps", heading_style),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DCE6F2"), spaceAfter=8),
    ]
    for line in recommendations.strip().split("\n"):
        clean_line = line.strip().lstrip("- ")
        if clean_line:
            content.append(Paragraph(f"- {clean_line}", body_style))
    content.extend(
        [
            Spacer(1, 16),
            Paragraph(
                "<i>This report is for screening purposes only and does not replace clinical diagnosis.</i>",
                disc_style,
            ),
        ]
    )
    doc.build(content)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def render_gauge(risk_prob):
    color = DANGER if risk_prob >= 50 else SUCCESS
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_prob,
            number={"suffix": "%", "font": {"size": 36, "color": INK}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": LINE, "tickfont": {"size": 11, "color": MUTE}},
                "bar": {"color": color, "thickness": 0.24},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": SUCCESS_SOFT},
                    {"range": [40, 70], "color": GOLD_SOFT},
                    {"range": [70, 100], "color": DANGER_SOFT},
                ],
                "threshold": {"line": {"color": INK, "width": 2}, "thickness": 0.75, "value": 50},
            },
        )
    )
    fig.update_layout(
        height=245,
        margin=dict(l=22, r=22, t=24, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Segoe UI"},
    )
    return fig


def render_symptom_chart(encoded):
    labels = [SYMPTOM_LABELS[key] for key in FEATURE_ORDER]
    values = [encoded[key] for key in FEATURE_ORDER]
    colorscale = [TEAL if value <= 0 else GOLD if value == 1 else CORAL for value in values]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colorscale, line=dict(width=0)),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_xaxes(range=[0, 2], tickvals=[0, 1, 2], gridcolor="#EEF2F7", zeroline=False)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=320,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=SLATE, family="Segoe UI", size=12),
        showlegend=False,
    )
    return fig


def severity_count(encoded):
    values = [encoded[key] for key in FEATURE_ORDER]
    return {
        "clear": sum(value == 0 for value in values),
        "watch": sum(value == 1 for value in values),
        "elevated": sum(value == 2 for value in values),
        "total": len(values),
        "score": int(sum(values)),
    }


# ===================== HEADER AND HERO =====================
st.markdown(
    """
<div class="app-shell">
    <div class="brand">
        <div class="brand-mark">PN</div>
        <div>
            <p class="brand-title">Postpartum Depression Screening</p>
            <p class="brand-subtitle">Professional maternal mental health decision support</p>
        </div>
    </div>
    <div class="status-bar"><span class="status-dot"></span>Model active</div>
</div>
""",
    unsafe_allow_html=True,
)

# Build the hero image markup up front so the picture renders inside the
# hero card itself instead of as a separate, unstyled st.image() below it.
hero_image_html = ""
if HERO_IMAGE.exists():
    encoded_hero = image_to_base64(HERO_IMAGE)
    if encoded_hero:
        hero_image_html = (
            f'<img src="data:image/png;base64,{encoded_hero}" '
            f'alt="Maternal wellbeing illustration" />'
        )

st.markdown(
    f"""
<section class="hero">
    <div class="hero-copy">
        <h1>Postpartum care insights in one clinical dashboard.</h1>
        <p>Review symptoms, estimate screening risk, visualize severity patterns, and create a printable report for follow-up conversations.</p>
        <div class="hero-actions">
            <span class="hero-chip"><span class="chip-mark"></span>Risk threshold 50%</span>
            <span class="hero-chip"><span class="chip-mark" style="background:#0F766E"></span>PDF report ready</span>
            <span class="hero-chip"><span class="chip-mark" style="background:#334E9B"></span>Local model inference</span>
        </div>
    </div>
    <div class="hero-image">{hero_image_html}</div>
</section>
""",
    unsafe_allow_html=True,
)


# ===================== FORM =====================
st.markdown(
    """
<div class="stats-grid">
    <div class="stat-card">
        <p class="stat-label">Workflow</p>
        <p class="stat-value">3 min</p>
        <p class="stat-note">Designed for a quick screening review.</p>
    </div>
    <div class="stat-card">
        <p class="stat-label">Inputs</p>
        <p class="stat-value">9</p>
        <p class="stat-note">Age and symptom indicators.</p>
    </div>
    <div class="stat-card">
        <p class="stat-label">Output</p>
        <p class="stat-value">Risk %</p>
        <p class="stat-note">Probability with clear next steps.</p>
    </div>
    <div class="stat-card">
        <p class="stat-label">Report</p>
        <p class="stat-value">PDF</p>
        <p class="stat-note">Downloadable screening summary.</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

left, right = st.columns([1.07, 0.93], gap="large")

with left:
    st.markdown(
        """
<div class="panel">
    <div class="panel-title">
        <h2>Screening intake</h2>
        <span>Step 1 of 2</span>
    </div>
    <p class="helper-copy">Enter the current observations. The dashboard will translate them into model-ready inputs and a visual symptom profile.</p>
""",
        unsafe_allow_html=True,
    )

    age_group = st.selectbox("Age group", list(AGE_MAP.keys()))

    st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        feeling_sad = st.selectbox("Feeling sad or tearful", ["No", "Sometimes", "Yes"])
        irritable = st.selectbox("Irritable towards baby and partner", ["No", "Sometimes", "Yes"])
        feeling_guilt = st.selectbox("Feeling of guilt", ["No", "Maybe", "Yes"])
        trouble_sleeping = st.selectbox("Trouble sleeping at night", ["No", "Two or more days a week", "Yes"])
    with c2:
        feeling_anxious = st.selectbox("Feeling anxious", ["No", "Yes"])
        problems_concentrating = st.selectbox("Problems concentrating or making decisions", ["No", "Often", "Yes"])
        bonding_issues = st.selectbox("Problems bonding with baby", ["No", "Sometimes", "Yes"])
        overeating = st.selectbox("Overeating or loss of appetite", ["No", "Sometimes", "Yes"])

    st.markdown("</div>", unsafe_allow_html=True)


encoded = {
    "Age": AGE_MAP[age_group],
    "Feeling sad or Tearful": SYMPTOM_MAP_3[feeling_sad],
    "Irritable towards baby & partner": SYMPTOM_MAP_3[irritable],
    "Trouble sleeping at night": SLEEP_MAP[trouble_sleeping],
    "Problems concentrating or making decision": CONC_MAP[problems_concentrating],
    "Overeating or loss of appetite": OVEREAT_MAP[overeating],
    "Feeling anxious": ANXIOUS_MAP[feeling_anxious],
    "Feeling of guilt": GUILT_MAP[feeling_guilt],
    "Problems of bonding with baby": SYMPTOM_MAP_3[bonding_issues],
}
summary = severity_count(encoded)
input_df = pd.DataFrame([encoded])

# Keep inputs as a named DataFrame all the way through (rather than calling
# .values), so column names line up with what the model/scaler were fitted
# on. Passing a bare numpy array can trigger a feature-name mismatch
# warning, or an outright error, on scikit-learn versions that validate
# feature names strictly.
if scaler is not None:
    try:
        scaled_values = scaler.transform(input_df)
        input_features = pd.DataFrame(scaled_values, columns=input_df.columns)
    except Exception as exc:
        st.error(f"The inputs could not be scaled: {exc}")
        st.stop()
else:
    input_features = input_df

with right:
    st.markdown(
        f"""
<div class="panel">
    <div class="panel-title">
        <h2>Live symptom profile</h2>
        <span>{summary["score"]}/16 score</span>
    </div>
    <div class="scale-row"><span>Clear</span><div class="scale-bar"><div class="scale-fill" style="width:{summary["clear"] / summary["total"] * 100:.0f}%"></div></div><strong>{summary["clear"]}</strong></div>
    <div class="scale-row"><span>Watch</span><div class="scale-bar"><div class="scale-fill" style="width:{summary["watch"] / summary["total"] * 100:.0f}%"></div></div><strong>{summary["watch"]}</strong></div>
    <div class="scale-row"><span>Elevated</span><div class="scale-bar"><div class="scale-fill" style="width:{summary["elevated"] / summary["total"] * 100:.0f}%"></div></div><strong>{summary["elevated"]}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.plotly_chart(render_symptom_chart(encoded), use_container_width=True, config={"displayModeBar": False})


st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(
    """
<div class="panel-title">
    <h2>Risk assessment</h2>
    <span>Step 2 of 2</span>
</div>
""",
    unsafe_allow_html=True,
)
run = st.button("Analyse depression risk", use_container_width=True, type="primary")

if run:
    try:
        probability = model.predict_proba(input_features)

        if probability.shape[1] < 2:
            st.error(
                "The model returned a single-class probability, so a risk "
                "percentage cannot be computed. Please check the model file."
            )
        else:
            risk_score = probability[0][1]
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
                result_class = "high"
                result_title = "High risk detected"
                result_sub = "Immediate clinical attention is recommended based on the model threshold."
            else:
                prediction_text = "Low Risk of Postpartum Depression"
                recommendations = (
                    "Continue routine postpartum monitoring.\n"
                    "Maintain healthy sleep and nutrition habits.\n"
                    "Attend regular health checkups.\n"
                    "Seek professional support if new symptoms arise."
                )
                result_class = "low"
                result_title = "Low risk"
                result_sub = "Continue routine monitoring and encourage support if symptoms change."

            st.markdown(
                f"""
<div class="result-card {result_class}">
    <p class="result-title {result_class}">{result_title}</p>
    <p class="result-sub">{result_sub}</p>
</div>
""",
                unsafe_allow_html=True,
            )

            chart_col, detail_col = st.columns([1.05, 0.95], gap="large")
            with chart_col:
                st.plotly_chart(render_gauge(risk_prob), use_container_width=True, config={"displayModeBar": False})
            with detail_col:
                st.markdown(
                    f"""
<table class="mini-table">
    <tr><td>Risk probability</td><td>{risk_prob}%</td></tr>
    <tr><td>Decision threshold</td><td>50%</td></tr>
    <tr><td>Age group</td><td>{age_group}</td></tr>
    <tr><td>Elevated signals</td><td>{summary["elevated"]}</td></tr>
</table>
""",
                    unsafe_allow_html=True,
                )

            st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
            st.markdown(
                """
<div class="panel-title">
    <h2>Recommended next steps</h2>
    <span>Clinician review</span>
</div>
""",
                unsafe_allow_html=True,
            )
            for index, line in enumerate(recommendations.strip().split("\n"), start=1):
                st.markdown(
                    f"""
<div class="rec-item">
    <div class="rec-num">{index}</div>
    <p>{line.strip()}</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            try:
                pdf_file = generate_pdf(age_group, prediction_text, risk_prob, recommendations)
                st.download_button(
                    label="Download full PDF report",
                    data=pdf_file,
                    file_name="postpartum_depression_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as exc:
                st.warning(f"The result is ready, but the PDF report could not be generated: {exc}")

    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
else:
    st.markdown(
        """
<p class="helper-copy">Run the assessment to see the probability gauge, risk decision, follow-up recommendations, and PDF export.</p>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="info-strip">
    <div class="info-icon">i</div>
    <p><strong>Medical disclaimer:</strong> This tool is intended for screening support only and does not replace clinical diagnosis or the judgement of a qualified healthcare professional.</p>
</div>
""",
    unsafe_allow_html=True,
)
