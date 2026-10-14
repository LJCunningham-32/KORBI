
import csv
import html
import textwrap
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# KORBI
# Knowledge & Operations Resource for Business Intelligence
# Sonoma State Athletics Business Operations
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_FOLDER = PROJECT_FOLDER / "Data"
PROCESSED_FOLDER = DATA_FOLDER / "Processed"


def korbi_file(filename):
    """
    Find a KORBI data file in either location:

    1. Data/Processed/<filename>  (normal local VS Code structure)
    2. <project root>/<filename>  (GitHub / Streamlit Cloud upload)

    This lets the same KORBI code run locally and in Streamlit Cloud
    without forcing the GitHub repository to mirror the local folders.
    """
    processed_path = PROCESSED_FOLDER / filename
    root_path = PROJECT_FOLDER / filename

    if processed_path.exists():
        return processed_path

    if root_path.exists():
        return root_path

    # If the file does not exist yet (for example the decision log),
    # choose a writable location appropriate for the current environment.
    if PROCESSED_FOLDER.exists():
        return processed_path

    return root_path


FILES = {
    "triage": korbi_file("korbi_bulk_triage_results.csv"),
    "decisions": korbi_file("korbi_management_decisions.csv"),
    "department": korbi_file("korbi_department_q1_snapshot.csv"),
    "budgets": korbi_file("korbi_category_budgets.csv"),
    "ledger": korbi_file("korbi_operational_ledger.csv"),
    "future": korbi_file("korbi_future_expenses.csv"),
    "funding": korbi_file("sonoma_funding_model.csv"),
    "staffing": korbi_file("sonoma_staffing_model.csv"),
    "financial_model": korbi_file("sonoma_financial_model_summary.csv"),
    "financial_history": korbi_file("sonoma_financial_history.csv"),
    "proposed_budget": korbi_file("sonoma_proposed_athletics_budget.csv"),
    "peer_comparison": korbi_file("eada_peer_comparison_2024.csv"),
    "team_benchmark": korbi_file("eada_team_benchmark_2024.csv"),
    "cost_drivers": korbi_file("eada_cost_drivers_2024.csv"),
    "team_summary": korbi_file("eada_team_summary_2024.csv"),
}

SIMULATION_DATE = "2027-10-01"

DECISION_FIELDS = [
    "request_id",
    "requestor_name",
    "program_code",
    "program_name",
    "category_code",
    "description",
    "priority",
    "amount",
    "korbi_recommendation",
    "financial_status",
    "annual_budget",
    "baseline_projected",
    "baseline_remaining",
    "baseline_percent",
    "projected_with_request",
    "remaining_with_request",
    "percent_with_request",
    "budget_impact_summary",
    "business_impact_summary",
    "risk_summary",
    "korbi_management_suggestion",
    "manager_decision",
    "decision_rationale",
    "requestor_email_response",
    "reviewed_by",
    "review_date",
    "decision_timestamp",
    "manager_notes",
    "next_action",
    "target_fiscal_year",
    "anticipated_next_year_budget",
]


# ============================================================
# PAGE SETUP / STYLE
# ============================================================

st.set_page_config(
    page_title="KORBI | Sonoma State Athletics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ssu-blue: #00539B;
        --ssu-blue-deep: #003B78;
        --ssu-navy: #102C49;
        --ssu-navy-2: #17365D;
        --ssu-sky: #ABCAE9;
        --ssu-bg: #EEF4FA;
        --ssu-card: #FFFFFF;
        --ssu-border: #D4E1EE;
        --ssu-text: #263746;
        --ssu-muted: #53697D;
        --good: #237A45;
        --monitor: #2F6FED;
        --warn: #A36F00;
        --risk: #C25A11;
        --bad: #B42318;
    }

    html, body, [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background-color: var(--ssu-bg);
        background-image:
            radial-gradient(circle at 88% 3%, rgba(0,83,155,.14), transparent 24rem),
            radial-gradient(circle at 18% 36%, rgba(171,202,233,.16), transparent 30rem),
            linear-gradient(135deg, rgba(0,83,155,.025) 25%, transparent 25%),
            linear-gradient(225deg, rgba(23,54,93,.02) 25%, transparent 25%);
        background-size: auto, auto, 32px 32px, 32px 32px;
        background-attachment: fixed;
    }

    .block-container {
        max-width: 1500px !important;
        padding-top: 4.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(255,255,255,.035), transparent 18%),
            linear-gradient(180deg, #082847 0%, #003B78 58%, #102C49 100%);
        border-right: 1px solid rgba(255,255,255,.12);
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: #17365D !important;
        -webkit-text-fill-color: #17365D !important;
        background: #FFFFFF !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: .48rem .58rem;
        border-radius: 9px;
        margin: .12rem 0;
        border: 1px solid transparent;
        transition: all .16s ease;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.11);
        border-color: rgba(255,255,255,.12);
        transform: translateX(2px);
    }

    /* Premium sidebar navigation contrast */
    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label * {
        color: #F7FBFF !important;
        -webkit-text-fill-color: #F7FBFF !important;
        font-weight: 750 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #0B67B2 0%, #00539B 100%) !important;
        border: 1px solid rgba(255,255,255,.28) !important;
        box-shadow: 0 5px 16px rgba(0,0,0,.20) !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 900 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        opacity: 1 !important;
    }

    .sidebar-brand {
        background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.18);
        border-radius: 14px;
        padding: .85rem .85rem .75rem;
        margin: .15rem 0 .8rem;
        box-shadow: 0 8px 22px rgba(0,0,0,.14);
    }
    .sidebar-brand .ssu-mark {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 1.05rem;
        font-weight: 950;
        letter-spacing: .06rem;
    }
    .sidebar-brand .ssu-sub {
        color: #CFE4F7 !important;
        -webkit-text-fill-color: #CFE4F7 !important;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08rem;
        text-transform: uppercase;
        margin-top: .15rem;
    }

    .korbi-header {
        background:
            linear-gradient(118deg, rgba(255,255,255,.06), transparent 28%),
            linear-gradient(120deg, #0B2945 0%, #004C97 58%, #17365D 100%);
        border-bottom: 4px solid #79AEDD;
        border-radius: 0 0 18px 18px;
        padding: 1.35rem 1.65rem 1.15rem;
        margin: -.95rem -1.15rem 1.35rem;
        box-shadow: 0 10px 28px rgba(16,44,73,.16);
        position: relative;
        overflow: hidden;
    }

    .korbi-header::after {
        content: "";
        position: absolute;
        right: -5rem;
        top: -4rem;
        width: 20rem;
        height: 12rem;
        transform: rotate(-18deg);
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.08), transparent);
        pointer-events: none;
    }

    .korbi-title {
        font-size: 2.7rem;
        font-weight: 950;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        line-height: .95;
        letter-spacing: -.04rem;
    }

    .korbi-subtitle {
        margin-top: .45rem;
        color: #E6F0FA !important;
        -webkit-text-fill-color: #E6F0FA !important;
        font-size: .96rem;
        font-weight: 650;
    }

    .korbi-brandline {
        margin-top: .55rem;
        color: #ABCAE9 !important;
        -webkit-text-fill-color: #ABCAE9 !important;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: .11rem;
        text-transform: uppercase;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--ssu-navy) !important;
        -webkit-text-fill-color: var(--ssu-navy) !important;
    }

    .section-title-wrap {
        margin: .15rem 0 1.1rem;
        padding-left: .85rem;
        border-left: 5px solid var(--ssu-blue);
    }

    .section-title-text {
        color: var(--ssu-navy) !important;
        -webkit-text-fill-color: var(--ssu-navy) !important;
        font-size: 1.9rem;
        line-height: 1.1;
        font-weight: 950;
        letter-spacing: -.025rem;
        margin: 0 0 .3rem 0;
    }

    .section-subtitle-text {
        color: #3C5368 !important;
        -webkit-text-fill-color: #3C5368 !important;
        font-size: .98rem;
        line-height: 1.5;
        font-weight: 650;
        opacity: 1 !important;
        max-width: 1180px;
    }

    [data-testid="stMetric"] {
        background:
            linear-gradient(180deg, rgba(0,83,155,.035), transparent 55%),
            #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-top: 4px solid var(--ssu-blue);
        border-radius: 13px;
        padding: .75rem .9rem;
        box-shadow: 0 6px 18px rgba(16,44,73,.065);
    }

    [data-testid="stMetric"] * {
        color: var(--ssu-navy) !important;
        -webkit-text-fill-color: var(--ssu-navy) !important;
    }

    .hero {
        background:
            radial-gradient(circle at 82% 18%, rgba(171,202,233,.18), transparent 19rem),
            linear-gradient(118deg, #0B2945 0%, #004C97 70%, #17365D 100%);
        border-radius: 20px;
        padding: 3.65rem 3.65rem;
        margin: .2rem 0 1.35rem;
        box-shadow: 0 18px 40px rgba(8,40,71,.18);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.1);
    }

    .hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            repeating-linear-gradient(
                118deg,
                transparent 0,
                transparent 44px,
                rgba(255,255,255,.028) 44px,
                rgba(255,255,255,.028) 48px
            );
        pointer-events: none;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 32rem;
        height: 8rem;
        right: -8rem;
        bottom: 1rem;
        transform: rotate(-18deg);
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.08), transparent);
        pointer-events: none;
    }

    .hero-inner {
        position: relative;
        z-index: 2;
        max-width: 1050px;
    }

    .hero-kicker {
        color: #ABCAE9 !important;
        -webkit-text-fill-color: #ABCAE9 !important;
        font-size: .78rem;
        font-weight: 950;
        letter-spacing: .17rem;
        text-transform: uppercase;
    }

    .hero-title {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: clamp(4.2rem, 7vw, 6.7rem);
        font-weight: 950;
        line-height: .88;
        letter-spacing: -.18rem;
        margin: .88rem 0 1.1rem;
        text-shadow: 0 6px 22px rgba(0,0,0,.15);
    }

    .hero-sub {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: clamp(1.45rem, 2.2vw, 2.05rem);
        font-weight: 800;
        line-height: 1.14;
        max-width: 920px;
    }

    .hero-body {
        color: #E3EFFA !important;
        -webkit-text-fill-color: #E3EFFA !important;
        max-width: 920px;
        font-size: 1.05rem;
        line-height: 1.68;
        margin-top: 1.2rem;
        font-weight: 560;
    }

    .value-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .9rem;
        margin: 0 0 1.85rem;
    }

    .value-card,
    .capability-card,
    .landing-panel,
    .section-card,
    .analysis-box {
        background:
            linear-gradient(180deg, rgba(0,83,155,.025), transparent 42%),
            #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-radius: 13px;
        box-shadow: 0 7px 20px rgba(16,44,73,.06);
    }

    .value-card {
        border-top: 4px solid var(--ssu-blue);
        padding: 1.15rem 1.2rem;
        transition: transform .16s ease, box-shadow .16s ease;
    }

    .value-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(16,44,73,.1);
    }

    .value-card .num {
        color: var(--ssu-blue) !important;
        -webkit-text-fill-color: var(--ssu-blue) !important;
        font-weight: 950;
        font-size: .72rem;
        letter-spacing: .14rem;
    }

    .value-card h3 {
        margin: .45rem 0 .5rem;
        font-size: 1.06rem;
        color: var(--ssu-navy) !important;
        -webkit-text-fill-color: var(--ssu-navy) !important;
        font-weight: 850;
    }

    .value-card p,
    .capability-card p,
    .landing-panel p {
        margin: 0;
        color: var(--ssu-text) !important;
        -webkit-text-fill-color: var(--ssu-text) !important;
        line-height: 1.58;
        font-size: .91rem;
        font-weight: 590;
        opacity: 1 !important;
    }

    .landing-panel {
        padding: 1.65rem 1.8rem;
        margin-bottom: 1rem;
    }

    .landing-eyebrow {
        color: var(--ssu-blue) !important;
        -webkit-text-fill-color: var(--ssu-blue) !important;
        font-size: .72rem;
        font-weight: 950;
        letter-spacing: .13rem;
        text-transform: uppercase;
        margin-bottom: .48rem;
    }

    .landing-panel h2 {
        margin: 0 0 .65rem;
        font-size: 1.55rem;
        font-weight: 900;
    }

    .capability-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem 1.15rem;
        margin: .7rem 0 1.8rem;
    }

    .capability-card {
        border-top: 4px solid var(--ssu-blue);
        padding: 1.05rem 1.1rem;
    }

    .capability-card h3 {
        margin: 0 0 .45rem 0;
        color: var(--ssu-navy) !important;
        -webkit-text-fill-color: var(--ssu-navy) !important;
        font-size: 1.05rem;
        font-weight: 850;
    }

    .support-card {
        background:
            radial-gradient(circle at 82% 20%, rgba(171,202,233,.18), transparent 16rem),
            linear-gradient(135deg,#102C49 0%,#00539B 100%);
        border-radius: 18px;
        padding: 1.65rem 2rem;
        margin: .75rem 0 1.2rem;
        box-shadow: 0 10px 26px rgba(16,44,73,.16);
        border: 1px solid rgba(255,255,255,.08);
    }

    .support-kicker {
        color: #ABCAE9 !important;
        -webkit-text-fill-color: #ABCAE9 !important;
        text-transform: uppercase;
        letter-spacing: .11rem;
        font-size: .78rem;
        font-weight: 900;
    }

    .support-value {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 3rem;
        font-weight: 950;
        margin-top: .25rem;
    }

    .support-copy {
        color: #E3EFFA !important;
        -webkit-text-fill-color: #E3EFFA !important;
        margin-top: .4rem;
        font-size: 1rem;
        font-weight: 600;
    }

    .analysis-box {
        border-left: 5px solid var(--ssu-blue);
        padding: 1rem 1.15rem;
        margin: .55rem 0 1rem;
    }

    .small-muted {
        color: var(--ssu-muted) !important;
        -webkit-text-fill-color: var(--ssu-muted) !important;
        font-size: .85rem;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--ssu-border);
        border-radius: 12px;
        overflow: hidden;
        background: #FFFFFF;
        box-shadow: 0 5px 18px rgba(16,44,73,.05);
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 9px !important;
        font-weight: 800 !important;
        min-height: 2.55rem !important;
        transition: transform .14s ease, box-shadow .14s ease, background .14s ease;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        background: linear-gradient(180deg, #0A62AE 0%, #00539B 100%) !important;
        border: 1px solid #004681 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        box-shadow: 0 4px 10px rgba(0,83,155,.16);
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(180deg, #00539B 0%, #003B78 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(0,83,155,.2);
    }

    .program-grid {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:.8rem;
        margin:.5rem 0 1.5rem 0;
    }

    .program-card {
        border:1px solid var(--ssu-border);
        border-left:5px solid var(--monitor);
        border-radius:12px;
        padding:.9rem 1rem;
        background:#EDF4FC;
        min-height:94px;
        box-shadow:0 5px 14px rgba(16,44,73,.045);
    }

    .program-card .sport {
        font-size:.74rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.03rem;
    }

    .program-card .status {
        font-size:1.18rem;
        font-weight:950;
        margin:.12rem 0 .2rem;
    }

    .program-card .detail {
        font-size:.82rem;
        line-height:1.3;
        color:#334E68 !important;
        -webkit-text-fill-color:#334E68 !important;
        font-weight:600;
    }

    .program-card.healthy {background:#EAF6EE;border-left-color:var(--good);}
    .program-card.healthy .sport,.program-card.healthy .status {color:var(--good) !important;-webkit-text-fill-color:var(--good) !important;}
    .program-card.monitor {background:#EAF2FB;border-left-color:var(--monitor);}
    .program-card.monitor .sport,.program-card.monitor .status {color:var(--monitor) !important;-webkit-text-fill-color:var(--monitor) !important;}
    .program-card.caution {background:#FFF7DA;border-left-color:var(--warn);}
    .program-card.caution .sport,.program-card.caution .status {color:var(--warn) !important;-webkit-text-fill-color:var(--warn) !important;}
    .program-card.highrisk {background:#FFF0E5;border-left-color:var(--risk);}
    .program-card.highrisk .sport,.program-card.highrisk .status {color:var(--risk) !important;-webkit-text-fill-color:var(--risk) !important;}
    .program-card.overbudget {background:#FDECEA;border-left-color:var(--bad);}
    .program-card.overbudget .sport,.program-card.overbudget .status {color:var(--bad) !important;-webkit-text-fill-color:var(--bad) !important;}

    .section-card {
        border-top:4px solid var(--ssu-blue);
        padding:1rem 1.05rem;
        height:100%;
    }

    .section-card .eyebrow {
        font-size:.72rem;
        font-weight:900;
        text-transform:uppercase;
        letter-spacing:.055rem;
        color:#64788A !important;
        -webkit-text-fill-color:#64788A !important;
    }

    .section-card .big {
        font-size:1.7rem;
        font-weight:950;
        color:var(--ssu-navy) !important;
        -webkit-text-fill-color:var(--ssu-navy) !important;
        margin:.15rem 0;
    }

    .decision-badge {
        display:inline-block;
        padding:.3rem .58rem;
        border-radius:999px;
        font-size:.72rem;
        font-weight:950;
        letter-spacing:.04rem;
    }

    .decision-approve {background:#EAF6EC;color:#237A45 !important;-webkit-text-fill-color:#237A45 !important;}
    .decision-defer {background:#FFF4D5;color:#8A6200 !important;-webkit-text-fill-color:#8A6200 !important;}
    .decision-deny {background:#FDECEA;color:#B42318 !important;-webkit-text-fill-color:#B42318 !important;}

    .korbi-table-wrap {
        overflow-x:auto;
        background:#FFFFFF;
        border:1px solid var(--ssu-border);
        border-radius:12px;
        margin:.5rem 0 1.25rem;
        box-shadow:0 5px 16px rgba(16,44,73,.055);
    }

    table.korbi-table {
        border-collapse:collapse;
        width:100%;
        min-width:760px;
        font-size:.84rem;
    }

    .korbi-table th {
        background:linear-gradient(180deg,#17365D 0%,#102C49 100%);
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
        text-align:left;
        padding:.74rem .78rem;
        white-space:nowrap;
        font-weight:850;
    }

    .korbi-table td {
        padding:.67rem .78rem;
        border-bottom:1px solid #E2EAF2;
        color:#26384A !important;
        -webkit-text-fill-color:#26384A !important;
        white-space:nowrap;
        background:#FFFFFF;
    }

    .korbi-table tr:nth-child(even) td {background:#F7FAFD;}
    .korbi-table tr:hover td {background:#EAF2FB;}
    .korbi-table .yes {color:#237A45 !important;font-weight:850;}
    .korbi-table .no {color:#7F8F9D !important;}

    .neutral-note,
    .benchmark-note,
    .premium-note {
        background:#FFFFFF;
        border:1px solid var(--ssu-border);
        border-left:4px solid var(--ssu-blue);
        border-radius:9px;
        padding:12px 14px;
        color:#263746 !important;
        -webkit-text-fill-color:#263746 !important;
        font-weight:620;
        line-height:1.55;
        box-shadow:0 3px 10px rgba(16,44,73,.035);
    }

    .benchmark-note {
        margin:.4rem 0 1rem;
        font-size:.9rem;
    }

    .neutral-note *,
    .benchmark-note *,
    .premium-note * {
        color:#263746 !important;
        -webkit-text-fill-color:#263746 !important;
    }

    .benchmark-note strong,
    .premium-note strong {
        color:var(--ssu-navy) !important;
        -webkit-text-fill-color:var(--ssu-navy) !important;
        font-weight:900;
    }

    .email-response-box {
        width:100% !important;
        box-sizing:border-box !important;
        background:#FFFFFF !important;
        color:#263746 !important;
        -webkit-text-fill-color:#263746 !important;
        border:1px solid var(--ssu-border) !important;
        border-left:4px solid var(--ssu-blue) !important;
        border-radius:10px !important;
        padding:1rem 1.1rem !important;
        margin:.35rem 0 .8rem 0 !important;
        font-family:Inter, ui-sans-serif, system-ui, sans-serif !important;
        font-size:.92rem !important;
        line-height:1.6 !important;
        font-weight:590 !important;
        white-space:pre-wrap !important;
        overflow-wrap:anywhere !important;
        word-break:break-word !important;
        overflow-x:hidden !important;
        box-shadow:0 4px 12px rgba(16,44,73,.04);
    }

    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] .stCaption,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] {
        color:#263746;
        -webkit-text-fill-color:#263746;
    }

    button[data-baseweb="tab"] {
        background:transparent !important;
        color:var(--ssu-navy) !important;
        -webkit-text-fill-color:var(--ssu-navy) !important;
        font-weight:780 !important;
    }

    button[data-baseweb="tab"] *,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] div {
        color:var(--ssu-navy) !important;
        -webkit-text-fill-color:var(--ssu-navy) !important;
        opacity:1 !important;
        font-weight:780 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] * {
        color:var(--ssu-blue) !important;
        -webkit-text-fill-color:var(--ssu-blue) !important;
        font-weight:900 !important;
    }

    /* Decision radio labels should stay readable on the light canvas. */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label *,
    [data-testid="stRadio"] p {
        color:var(--ssu-navy) !important;
        -webkit-text-fill-color:var(--ssu-navy) !important;
        font-weight:700 !important;
    }

    /* White text only on intentionally dark surfaces. */
    .hero-title,
    .hero-sub,
    .korbi-title,
    .support-value,
    .korbi-table th,
    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
    }

    @media (max-width: 900px) {
        .value-grid {grid-template-columns:repeat(2,1fr);}
        .program-grid {grid-template-columns:1fr;}
        .capability-grid {grid-template-columns:1fr;}
        .hero {padding:2.8rem 2rem;}
        .hero-title {letter-spacing:-.08rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def wrapped_email_box(text):
    safe_text = html.escape(str(text))
    st.markdown(
        f'<div class="email-response-box">{safe_text}</div>',
        unsafe_allow_html=True,
    )

def safe_float(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def money(value):
    value = safe_float(value)
    if abs(value) < 0.005:
        return "-"
    if value < 0:
        return f"(${abs(value):,.0f})"
    return f"${value:,.0f}"


def money_zero(value):
    """Currency formatter that displays zero as $0 instead of a dash."""
    value = safe_float(value)
    if value < 0:
        return f"(${abs(value):,.0f})"
    return f"${value:,.0f}"


def compact_money(value):
    value = safe_float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}${value / 1_000:.1f}K"
    return f"{sign}${value:,.0f}"


def pct(value):
    return f"{safe_float(value):.1f}%"


def read_df(path):
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def read_rows(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_decisions(rows):
    # Keep the current Streamlit session immediately consistent, even on
    # hosted environments where the local filesystem may be temporary.
    normalized = []
    for row in rows:
        normalized.append({field: row.get(field, "") for field in DECISION_FIELDS})
    st.session_state["_korbi_decision_records"] = normalized

    try:
        PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
        with open(FILES["decisions"], "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=DECISION_FIELDS)
            writer.writeheader()
            writer.writerows(normalized)
    except OSError:
        # Session state still keeps the prototype functional for the active session.
        pass


def load_decision_rows():
    if "_korbi_decision_records" not in st.session_state:
        st.session_state["_korbi_decision_records"] = read_rows(FILES["decisions"])
    return st.session_state["_korbi_decision_records"]


def load_decisions():
    return {
        str(r.get("request_id", "")): r
        for r in load_decision_rows()
        if r.get("request_id")
    }


def current_decision_df():
    rows = load_decision_rows()
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=DECISION_FIELDS)


DEFERRED_FUTURE_SEED = [
    {
        "Request ID": "DF-001",
        "Program": "Men's Soccer",
        "Purchase Request": "Portable recovery cold tubs",
        "Deferred Amount": 4200,
        "Reason Deferred": "Current-year approval would reduce remaining flexibility below a comfortable operating reserve.",
        "Next Step": "Elevate to AD if operationally necessary; otherwise carry forward.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 4500,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-002",
        "Program": "Women's Soccer",
        "Purchase Request": "Additional GPS athlete-tracking units",
        "Deferred Amount": 6800,
        "Reason Deferred": "Not essential for current-year competition; travel and core operating needs take priority.",
        "Next Step": "Carry forward to next budget cycle.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 7200,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-003",
        "Program": "Men's Basketball",
        "Purchase Request": "Additional video-analysis hardware",
        "Deferred Amount": 9500,
        "Reason Deferred": "Existing system remains functional; higher-priority competition and travel costs were retained.",
        "Next Step": "Reprice and include in next-year operating plan.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 10000,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-004",
        "Program": "Women's Basketball",
        "Purchase Request": "Locker room equipment refresh",
        "Deferred Amount": 12000,
        "Reason Deferred": "Capital-style improvement deferred to protect current-year operating capacity.",
        "Next Step": "Evaluate for next-year budget or alternative funding.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 12600,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-005",
        "Program": "Baseball",
        "Purchase Request": "Portable batting cage upgrades",
        "Deferred Amount": 8750,
        "Reason Deferred": "Useful but not immediately required for competition readiness.",
        "Next Step": "Include in next-year equipment planning.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 9200,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-006",
        "Program": "Softball",
        "Purchase Request": "Bullpen / training equipment package",
        "Deferred Amount": 7400,
        "Reason Deferred": "Current-year equipment allocation is limited and core competition needs take priority.",
        "Next Step": "Carry forward and revalidate need before budget submission.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 7800,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-007",
        "Program": "Men's Cross Country",
        "Purchase Request": "Additional travel support package",
        "Deferred Amount": 5600,
        "Reason Deferred": "Current-year travel budget is already committed to scheduled competition.",
        "Next Step": "Include in next-year travel budget assumptions.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 5900,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-008",
        "Program": "Women's Volleyball",
        "Purchase Request": "Practice technology package",
        "Deferred Amount": 6250,
        "Reason Deferred": "Deferred behind core competition, travel, and equipment requirements.",
        "Next Step": "Reassess technology need during next-year budget build.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 6600,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-009",
        "Program": "Men's Golf",
        "Purchase Request": "Tournament analytics software",
        "Deferred Amount": 3800,
        "Reason Deferred": "Current-year approval depends on another funding source; otherwise it moves to next year's plan.",
        "Next Step": "Seek alternative funding; carry forward if unfunded.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 4000,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
    {
        "Request ID": "DF-010",
        "Program": "Athletics Administration",
        "Purchase Request": "Shared recruiting / operations software",
        "Deferred Amount": 14000,
        "Reason Deferred": "Department-wide software purchase deferred until annual technology priorities are reviewed.",
        "Next Step": "Evaluate as a shared-services budget item for next year.",
        "Target Fiscal Year": "FY 2028-29",
        "Anticipated FY Budget": 14700,
        "Status": "Carried Forward",
        "Source": "Simulated Planning Seed",
    },
]


def deferred_future_needs_df():
    rows = [dict(r) for r in DEFERRED_FUTURE_SEED]
    decisions = current_decision_df()

    if not decisions.empty and "manager_decision" in decisions.columns:
        deferred = decisions[
            decisions["manager_decision"].astype(str).str.upper() == "DEFER"
        ].copy()

        for _, record in deferred.iterrows():
            amount = safe_float(record.get("amount"))
            target_fy = str(record.get("target_fiscal_year", "")).strip()
            if not target_fy or target_fy.lower() == "nan":
                target_fy = "FY 2027-28"

            anticipated = safe_float(record.get("anticipated_next_year_budget"))
            if anticipated <= 0 and target_fy == "FY 2028-29":
                anticipated = round(amount * 1.05, -1)

            next_action = str(record.get("next_action", "")).strip()
            if not next_action or next_action.lower() == "nan":
                next_action = (
                    "Reconsider later this fiscal year; elevate to the Director of Athletics "
                    "if operationally necessary."
                )

            reason = str(record.get("decision_rationale", "")).strip()
            if not reason or reason.lower() == "nan":
                reason = str(record.get("budget_impact_summary", "")).strip()

            rows.append({
                "Request ID": str(record.get("request_id", "")),
                "Program": str(record.get("program_name", "")),
                "Purchase Request": str(record.get("description", "")),
                "Deferred Amount": amount,
                "Reason Deferred": reason,
                "Next Step": next_action,
                "Target Fiscal Year": target_fy,
                "Anticipated FY Budget": anticipated if anticipated > 0 else amount,
                "Status": "Carried Forward" if target_fy == "FY 2028-29" else "Deferred",
                "Source": "Live KORBI Decision",
            })

    return pd.DataFrame(rows)


def first_existing_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def section_title(title, subtitle=None):
    st.markdown(
        f'<div class="section-title-wrap"><div class="section-title-text">{html.escape(str(title))}</div>'
        + (f'<div class="section-subtitle-text">{html.escape(str(subtitle))}</div>' if subtitle else '')
        + '</div>',
        unsafe_allow_html=True,
    )


def accounting_table(df, currency_cols=None, percent_cols=None):
    if df is None or df.empty:
        return df

    out = df.copy()
    currency_cols = currency_cols or []
    percent_cols = percent_cols or []

    for col in currency_cols:
        if col in out.columns:
            out[col] = out[col].apply(money)

    for col in percent_cols:
        if col in out.columns:
            out[col] = out[col].apply(
                lambda x: "-" if abs(safe_float(x)) < 0.005 else f"{safe_float(x):.1f}%"
            )

    return out


def dataframe_download(df, filename, label):
    if df is None or df.empty:
        return
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        width="stretch",
    )


# ============================================================
# DATA LOAD
# ============================================================

triage_df = read_df(FILES["triage"])
decision_df = current_decision_df()
department_df = read_df(FILES["department"])
budget_df = read_df(FILES["budgets"])
ledger_df = read_df(FILES["ledger"])
future_df = read_df(FILES["future"])
funding_df = read_df(FILES["funding"])
staffing_df = read_df(FILES["staffing"])
financial_model_df = read_df(FILES["financial_model"])
financial_history_df = read_df(FILES["financial_history"])
proposed_budget_df = read_df(FILES["proposed_budget"])
peer_comparison_df = read_df(FILES["peer_comparison"])
team_benchmark_df = read_df(FILES["team_benchmark"])
cost_drivers_df = read_df(FILES["cost_drivers"])
team_summary_df = read_df(FILES["team_summary"])

reviewed_ids = set()
if not decision_df.empty and "request_id" in decision_df.columns:
    reviewed_ids = set(decision_df["request_id"].astype(str))

if not triage_df.empty and "request_id" in triage_df.columns:
    triage_df["reviewed"] = triage_df["request_id"].astype(str).isin(reviewed_ids)


# ============================================================
# REQUEST / FINANCIAL LOGIC
# ============================================================

def category_context(row):
    category = str(row.get("category_code", "")).upper()
    priority = str(row.get("priority", "")).upper()

    if category == "TRAV":
        return (
            "This request affects team travel and competition operations. "
            "Airfare, lodging, transportation, and event schedules can make these costs time-sensitive."
        )
    if category == "MIE":
        return (
            "This request affects meals and incidental expenses tied to team travel "
            "and should align with the approved travel plan and per diem policy."
        )
    if category == "FAC":
        return (
            "This request affects a field, facility, or competition space and may affect "
            "safety, practice availability, or event readiness."
        )
    if category == "TECH":
        return (
            "This request affects technology, analytics, software, or performance systems. "
            "Recurring licensing or renewal costs should also be considered."
        )
    if category == "UNIF":
        return "This request affects uniforms or apparel needed for team operations and competition."
    if category == "OPS":
        return (
            "This request affects team or event operations required to conduct practices, games, "
            "or the competitive season."
        )
    if category == "EQUIP":
        if priority == "CRITICAL":
            return (
                "This request affects equipment required for safe or continuous team operations. "
                "Delay may create safety or continuity risk."
            )
        if priority == "NECESSARY":
            return (
                "This request addresses worn, aging, damaged, or operationally important equipment. "
                "Delay may increase reliability or replacement risk."
            )
        return (
            "This equipment request may improve performance or student-athlete experience, "
            "but current operations can generally continue without immediate purchase."
        )

    return "This request affects general program operations."


def budget_impact(row):
    amount = safe_float(row.get("amount"))
    annual = safe_float(row.get("annual_budget"))
    before_remaining = safe_float(row.get("baseline_remaining"))
    after_remaining = safe_float(row.get("remaining_with_request"))
    before_pct = safe_float(row.get("baseline_percent"))
    after_pct = safe_float(row.get("percent_with_request"))

    request_pct = amount / annual * 100 if annual else 0
    cushion_used = amount / before_remaining * 100 if before_remaining > 0 else 100.0

    if after_remaining < 0:
        return (
            f"The {money(amount)} request equals {request_pct:.1f}% of the annual operating budget. "
            f"Projected utilization rises from {before_pct:.1f}% to {after_pct:.1f}%. "
            f"It eliminates the remaining cushion and creates a projected deficit of "
            f"{money(abs(after_remaining))}."
        )

    return (
        f"The {money(amount)} request equals {request_pct:.1f}% of the annual operating budget. "
        f"Projected utilization rises from {before_pct:.1f}% to {after_pct:.1f}%. "
        f"The projected cushion falls from {money(before_remaining)} to {money(after_remaining)}, "
        f"using about {cushion_used:.1f}% of the program's remaining financial flexibility."
    )


def coach_impact(row):
    baseline_remaining = pd.to_numeric(
        row.get("baseline_remaining", 0),
        errors="coerce"
    )

    remaining_with_request = pd.to_numeric(
        row.get("remaining_with_request", 0),
        errors="coerce"
    )

    if pd.isna(baseline_remaining):
        baseline_remaining = 0

    if pd.isna(remaining_with_request):
        remaining_with_request = 0

    flexibility_reduction = max(
        0,
        baseline_remaining - remaining_with_request
    )

    flexibility_reduction_pct = (
        (flexibility_reduction / baseline_remaining) * 100
        if baseline_remaining > 0
        else 0
    )

    return (
        f"This request can be evaluated within the current program budget, "
        f"but it would reduce projected year-end flexibility from "
        f"${baseline_remaining:,.0f} to ${remaining_with_request:,.0f}. "
        f"That represents a {flexibility_reduction_pct:.1f}% reduction "
        f"in remaining flexibility. "
        f"KORBI does not assume what the program may need later; it shows "
        f"the trade-off so the coach can decide whether this expense is worth "
        f"reducing capacity for future travel, equipment, or other unplanned requirements."
    )

def risk_summary(row):
    after_pct = safe_float(row.get("percent_with_request"))
    remaining = safe_float(row.get("remaining_with_request"))
    priority = str(row.get("priority", "")).upper()

    if after_pct > 100:
        return (
            "HIGH FINANCIAL RISK. Approval would place the program over its projected annual operating "
            "budget and require an offset, transfer, or alternative funding source."
        )
    if after_pct >= 95:
        return (
            f"HIGH FINANCIAL RISK. Only {money(remaining)} would remain. Unexpected travel, competition, "
            "equipment, or operating costs could push the program over budget."
        )
    if after_pct >= 90:
        return (
            "MODERATE-HIGH FINANCIAL RISK. The request remains within budget, but the program would move "
            "into a tight financial position."
        )
    if after_pct >= 80 and priority == "ENHANCEMENT":
        return (
            "MODERATE FINANCIAL RISK. The request fits, but it is discretionary and reduces flexibility "
            "available for required costs later in the year."
        )
    if after_pct >= 80:
        return (
            "MODERATE FINANCIAL RISK. The purchase fits within the current forecast, but remaining "
            "seasonal obligations should continue to be monitored."
        )

    return (
        "LOWER FINANCIAL RISK. The forecast indicates adequate capacity remains after the request, "
        "subject to normal procurement and operational review."
    )


def actionable_recommendation(row):
    after_pct = safe_float(row.get("percent_with_request"))
    remaining = safe_float(row.get("remaining_with_request"))
    amount = safe_float(row.get("amount"))
    priority = str(row.get("priority", "")).upper()
    category = str(row.get("category_code", "")).upper()

    if after_pct > 100:
        if priority == "CRITICAL":
            return (
                "ESCALATE — CRITICAL NEED REQUIRES A FUNDING SOURCE",
                f"Do not fund the {money(amount)} request from the current allocation without an offset, "
                "transfer, or alternative funding source. Because the need is critical, escalate rather than simply deny it."
            )
        return (
            "DENY OR DEFER — REQUEST CREATES A PROJECTED DEFICIT",
            "Do not approve from the current operating budget. Identify savings, reduce scope, "
            "use another funding source, or reconsider if the forecast improves."
        )

    if after_pct >= 95:
        if priority == "CRITICAL":
            return (
                "APPROVE ONLY WITH SENIOR MANAGEMENT REVIEW",
                f"The critical need may justify the purchase, but only {money(remaining)} would remain. "
                "Confirm remaining obligations and contingency funding first."
            )
        if priority == "NECESSARY":
            return (
                "DEFER UNLESS OFFSETTING SAVINGS ARE IDENTIFIED",
                f"The request addresses a legitimate need, but only {money(remaining)} would remain. "
                f"Confirm remaining obligations or identify savings equal to at least {money(amount)}."
            )
        return (
            "DEFER — PRESERVE REMAINING BUDGET CAPACITY",
            "The enhancement would leave too little flexibility for required seasonal costs."
        )

    if after_pct >= 90:
        if priority == "CRITICAL":
            return (
                "APPROVE — MONITOR REMAINING OBLIGATIONS",
                "The request supports a critical need and remains within budget. "
                "Confirm scheduled travel and other required costs remain funded."
            )
        if priority == "NECESSARY":
            return (
                "APPROVE ONLY AFTER REMAINING COSTS ARE CONFIRMED",
                "The need appears legitimate, but the program would move into a tight position."
            )
        return (
            "DEFER — BUSINESS VALUE DOES NOT OUTWEIGH CURRENT BUDGET RISK",
            "The enhancement would materially reduce year-end flexibility."
        )

    if after_pct >= 80:
        if priority == "CRITICAL":
            return (
                "APPROVE — ADEQUATE CAPACITY REMAINS",
                "The request addresses a critical need and the program retains reasonable forecasted capacity afterward."
            )
        if priority == "NECESSARY":
            return (
                "APPROVE WITH BUDGET MONITORING",
                "The purchase addresses a necessary need and fits within the forecast."
            )
        return (
            "CONSIDER — REQUIRE CLEAR OPERATIONAL VALUE",
            "The enhancement fits financially, but approval should depend on whether the benefit is worth reducing the remaining cushion."
        )

    if priority == "CRITICAL":
        return (
            "APPROVE — FINANCIAL CAPACITY SUPPORTS THE NEED",
            "The request addresses a critical operational requirement and adequate forecasted capacity remains."
        )
    if priority == "NECESSARY":
        return (
            "APPROVE — FINANCIAL CAPACITY REMAINS HEALTHY",
            "The purchase addresses a necessary operating requirement and the program retains a healthy projected cushion."
        )
    if category == "TECH":
        return (
            "CONSIDER — VERIFY VALUE AND RECURRING COSTS",
            "The program has capacity for the enhancement. Confirm measurable value and any future subscription, licensing, or renewal costs."
        )
    return (
        "CONSIDER — FINANCIALLY AFFORDABLE",
        "The program has sufficient forecasted capacity. Approval should depend on operational value relative to other uses of the remaining budget."
    )


def requestor_name(row):
    for key in [
        "requestor_name", "requestor", "requester_name", "requester",
        "coach_name", "coach", "submitted_by", "requested_by"
    ]:
        value = str(row.get(key, "")).strip()
        if value and value.lower() not in {"nan", "none"}:
            return value
    return ""


def decision_rationale(row, decision, next_action="", target_fiscal_year="", anticipated_next_year_budget=0):
    decision = str(decision).upper().strip()
    amount = safe_float(row.get("amount"))
    program = str(row.get("program_name", "the program"))
    description = str(row.get("description", "the request"))
    priority = str(row.get("priority", "")).upper()
    before_pct = safe_float(row.get("baseline_percent"))
    after_pct = safe_float(row.get("percent_with_request"))
    before_remaining = safe_float(row.get("baseline_remaining"))
    after_remaining = safe_float(row.get("remaining_with_request"))

    if decision == "APPROVE":
        if after_remaining < 0:
            return (
                f"The {money(amount)} request for {description} was approved as a management exception despite "
                f"a projected deficit of {money(abs(after_remaining))}. Approval requires an offset, transfer, "
                f"or alternative funding source and should be tracked as an exception to the current operating plan."
            )
        return (
            f"The {money(amount)} request for {description} was approved because it can be supported within the "
            f"current {program} forecast. Projected utilization moves from {before_pct:.1f}% to {after_pct:.1f}% "
            f"and projected year-end flexibility changes from {money(before_remaining)} to {money(after_remaining)}. "
            f"The approval recognizes the operating value of the request while retaining visibility into the reduced cushion."
        )

    if decision == "DEFER":
        rationale = (
            f"The {money(amount)} request for {description} was deferred because approving it now would move "
            f"{program} from {before_pct:.1f}% to {after_pct:.1f}% projected utilization and reduce projected "
            f"year-end flexibility from {money(before_remaining)} to {money(after_remaining)}. The need may be valid, "
            f"but preserving capacity for remaining travel, equipment, and other operating requirements is the stronger "
            f"financial decision at this point."
        )

        if next_action:
            rationale += f" Recommended next step: {next_action}."

        if target_fiscal_year:
            rationale += f" Planning target: {target_fiscal_year}."

        if safe_float(anticipated_next_year_budget) > 0:
            rationale += (
                f" Anticipated budget requirement for that cycle: "
                f"{money(anticipated_next_year_budget)}."
            )

        return rationale

    # DENY
    if after_remaining < 0 or after_pct > 100:
        return (
            f"The {money(amount)} request for {description} was denied because it would push {program} beyond its "
            f"projected annual operating capacity. The request would result in {after_pct:.1f}% projected utilization "
            f"and a projected deficit of {money(abs(after_remaining))}. No offsetting savings or alternative funding "
            f"source is currently identified."
        )
    return (
        f"The {money(amount)} request for {description} was denied because the expected operating value does not "
        f"justify reducing {program}'s projected year-end flexibility from {money(before_remaining)} to "
        f"{money(after_remaining)} at this time. The funds should remain available for higher-priority or unplanned "
        f"requirements later in the year."
    )


def requestor_email(row, decision, name="", notes="", next_action="", target_fiscal_year="", anticipated_next_year_budget=0):
    decision = str(decision).upper().strip()
    amount = safe_float(row.get("amount"))
    description = str(row.get("description", "request"))
    program = str(row.get("program_name", "program"))
    before_pct = safe_float(row.get("baseline_percent"))
    after_pct = safe_float(row.get("percent_with_request"))
    before_remaining = safe_float(row.get("baseline_remaining"))
    after_remaining = safe_float(row.get("remaining_with_request"))
    greeting = f"{name}," if name else "Hello,"

    if decision == "APPROVE":
        body = (
            f"I reviewed your {money(amount)} request for {description}. The request is approved. "
            f"Based on the current {program} forecast, projected budget utilization moves from "
            f"{before_pct:.1f}% to {after_pct:.1f}%, leaving approximately {money(after_remaining)} in projected "
            f"year-end flexibility. Please proceed through the normal purchasing process and keep any material "
            f"changes to cost or scope visible before committing additional funds."
        )
    elif decision == "DEFER":
        body = (
            f"I reviewed your {money(amount)} request for {description}. The request is being deferred for now. "
            f"Approving it at this point would move the {program} budget from {before_pct:.1f}% to {after_pct:.1f}% "
            f"projected utilization and reduce projected year-end flexibility from {money(before_remaining)} to "
            f"{money(after_remaining)}. That would leave less room for remaining travel, equipment, or other unexpected "
            f"operating needs."
        )
        if next_action:
            body += f" The next step is to {next_action[0].lower() + next_action[1:] if len(next_action) > 1 else next_action.lower()}."
        if target_fiscal_year == "FY 2028-29":
            body += (
                f" If the need remains valid, it will also be tracked for the {target_fiscal_year} budget cycle"
                + (
                    f" at an anticipated planning amount of {money(anticipated_next_year_budget)}."
                    if safe_float(anticipated_next_year_budget) > 0 else "."
                )
            )
    else:
        if after_remaining < 0 or after_pct > 100:
            body = (
                f"I reviewed your {money(amount)} request for {description}. The request is denied under the current "
                f"budget because it would move the {program} forecast to {after_pct:.1f}% utilization and create a "
                f"projected deficit of approximately {money(abs(after_remaining))}. If another funding source or an "
                f"offsetting reduction is identified, the request can be reconsidered as a new funding decision."
            )
        else:
            body = (
                f"I reviewed your {money(amount)} request for {description}. The request is denied at this time because "
                f"the expected value does not justify reducing projected year-end flexibility from {money(before_remaining)} "
                f"to {money(after_remaining)}. We need to preserve that capacity for higher-priority and unplanned operating "
                f"requirements later in the year."
            )

    if notes.strip():
        body += f"\n\nAdditional context: {notes.strip()}"

    return f"{greeting}\n\n{body}\n\nThank you."


def approved_decision_adjustments(program_name=None, exclude_request_id=None):
    decisions = current_decision_df()
    if decisions.empty or "manager_decision" not in decisions.columns:
        return 0.0

    approved = decisions[
        decisions["manager_decision"].astype(str).str.upper() == "APPROVE"
    ].copy()

    if program_name and "program_name" in approved.columns:
        approved = approved[
            approved["program_name"].astype(str) == str(program_name)
        ]

    if exclude_request_id and "request_id" in approved.columns:
        approved = approved[
            approved["request_id"].astype(str) != str(exclude_request_id)
        ]

    if "amount" not in approved.columns:
        return 0.0

    return pd.to_numeric(approved["amount"], errors="coerce").fillna(0).sum()


def live_request_row(row):
    """Recalculate a request against decisions already approved in this simulation."""
    live = dict(row)
    program = str(live.get("program_name", ""))
    request_id = str(live.get("request_id", ""))
    amount = safe_float(live.get("amount"))
    annual = safe_float(live.get("annual_budget"))
    base_projected = safe_float(live.get("baseline_projected"))
    base_open = safe_float(live.get("open_pos"))

    added = approved_decision_adjustments(
        program_name=program,
        exclude_request_id=request_id,
    )

    current_projected = base_projected + added
    current_remaining = annual - current_projected
    current_pct = (current_projected / annual * 100) if annual else 0.0
    projected_with = current_projected + amount
    remaining_with = annual - projected_with
    pct_with = (projected_with / annual * 100) if annual else 0.0

    live["open_pos"] = base_open + added
    live["baseline_projected"] = current_projected
    live["baseline_remaining"] = current_remaining
    live["baseline_percent"] = current_pct
    live["projected_with_request"] = projected_with
    live["remaining_with_request"] = remaining_with
    live["percent_with_request"] = pct_with
    return live


def save_decision(row, recommendation, suggestion, decision, reviewer, notes, requestor="", next_action="", target_fiscal_year="", anticipated_next_year_budget=0):
    decisions = load_decisions()
    rationale = decision_rationale(
        row,
        decision,
        next_action=next_action,
        target_fiscal_year=target_fiscal_year,
        anticipated_next_year_budget=anticipated_next_year_budget,
    )
    email_text = requestor_email(
        row,
        decision,
        requestor,
        notes,
        next_action=next_action,
        target_fiscal_year=target_fiscal_year,
        anticipated_next_year_budget=anticipated_next_year_budget,
    )

    record = {
        "request_id": row.get("request_id", ""),
        "requestor_name": requestor or requestor_name(row),
        "program_code": row.get("program_code", ""),
        "program_name": row.get("program_name", ""),
        "category_code": row.get("category_code", ""),
        "description": row.get("description", ""),
        "priority": row.get("priority", ""),
        "amount": row.get("amount", ""),
        "korbi_recommendation": recommendation,
        "financial_status": row.get("financial_status", ""),
        "annual_budget": row.get("annual_budget", ""),
        "baseline_projected": row.get("baseline_projected", ""),
        "baseline_remaining": row.get("baseline_remaining", ""),
        "baseline_percent": row.get("baseline_percent", ""),
        "projected_with_request": row.get("projected_with_request", ""),
        "remaining_with_request": row.get("remaining_with_request", ""),
        "percent_with_request": row.get("percent_with_request", ""),
        "budget_impact_summary": budget_impact(row),
        "business_impact_summary": category_context(row),
        "risk_summary": risk_summary(row),
        "korbi_management_suggestion": suggestion,
        "manager_decision": decision,
        "decision_rationale": rationale,
        "requestor_email_response": email_text,
        "reviewed_by": reviewer,
        "review_date": SIMULATION_DATE,
        "decision_timestamp": datetime.now().isoformat(timespec="seconds"),
        "manager_notes": notes,
        "next_action": next_action,
        "target_fiscal_year": target_fiscal_year,
        "anticipated_next_year_budget": anticipated_next_year_budget,
    }

    decisions[str(row.get("request_id", ""))] = record
    write_decisions(list(decisions.values()))
    return record


def _base_program_metrics(program_name):
    """Raw program-level source values before saved purchase approvals are layered in."""
    if triage_df.empty or "program_name" not in triage_df.columns:
        return None

    rows = triage_df[triage_df["program_name"].astype(str) == str(program_name)]
    if rows.empty:
        return None

    row = rows.iloc[0]
    annual = safe_float(row.get("annual_budget"))
    actual = safe_float(row.get("q1_actuals"))
    committed = safe_float(row.get("open_pos"))
    projected = safe_float(row.get("baseline_projected"))

    # A connected model can never project less than what is already actual + committed.
    projected = max(projected, actual + committed)

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "projected": projected,
    }


def program_metrics(program_name):
    base = _base_program_metrics(program_name)
    if not base:
        return None

    approved_adjustment = approved_decision_adjustments(program_name)
    annual = base["annual"]
    actual = base["actual"]
    committed = base["committed"] + approved_adjustment
    projected = max(base["projected"] + approved_adjustment, actual + committed)
    remaining_forecast = max(projected - actual - committed, 0)
    remaining = annual - projected
    utilization = (projected / annual * 100) if annual else 0.0
    unallocated = annual - actual - committed

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "approved_decision_adjustment": approved_adjustment,
        "remaining_forecast": remaining_forecast,
        "unallocated": unallocated,
        "projected": projected,
        "remaining": remaining,
        "utilization": utilization,
    }

def program_health(utilization):
    """Single health rule used everywhere KORBI displays program status."""
    util = safe_float(utilization)
    if util > 100:
        return "OVER BUDGET", "overbudget"
    if util >= 95:
        return "HIGH RISK", "highrisk"
    if util >= 90:
        return "CAUTION", "caution"
    if util >= 80:
        return "MONITOR", "monitor"
    return "HEALTHY", "healthy"



# ============================================================
# SIMULATED APPROVED PURCHASE ORDERS / DENIED REQUESTS
# ============================================================

PO_TEMPLATES = {
    "basketball": [
        ("Travel", "Team hotel block", "Marriott / Hilton", 0.18),
        ("Travel", "Team air / ground transportation", "Southwest / Charter Vendor", 0.15),
        ("Meals / Per Diem", "Competition meals and per diem", "Team Travel", 0.10),
        ("Competition Operations", "Officials and game operations", "CCAA / Officials", 0.12),
        ("Equipment & Supplies", "Uniforms and competition equipment", "Nike / BSN Sports", 0.12),
        ("Equipment & Supplies", "Basketballs and training equipment", "Wilson / BSN Sports", 0.07),
        ("Technology / Software", "Video analysis and scouting platform", "Hudl / Synergy", 0.07),
        ("Recruiting", "Recruiting travel and prospect evaluation", "Recruiting Travel", 0.07),
        ("Facilities / Rentals", "Practice / event operations support", "Campus Operations", 0.07),
        ("Other Program Operations", "Medical and recovery supplies", "Performance Health", 0.05),
    ],
    "soccer": [
        ("Travel", "Away match hotel block", "Marriott / Hilton", 0.18),
        ("Travel", "Team bus transportation", "Charter Bus Vendor", 0.14),
        ("Meals / Per Diem", "Competition meals and per diem", "Team Travel", 0.11),
        ("Competition Operations", "Officials and match operations", "CCAA / Officials", 0.11),
        ("Equipment & Supplies", "Uniforms and training apparel", "Nike / BSN Sports", 0.10),
        ("Equipment & Supplies", "Balls, goals, and field equipment", "Kwik Goal / BSN Sports", 0.09),
        ("Technology / Software", "Video and athlete-performance platform", "Hudl", 0.07),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.07),
        ("Facilities / Rentals", "Field and event support", "Campus Operations", 0.07),
        ("Other Program Operations", "Recovery and medical supplies", "Performance Health", 0.06),
    ],
    "cross country": [
        ("Travel", "Meet hotel blocks", "Marriott / Hilton", 0.22),
        ("Travel", "Team transportation", "Charter / Rental Vehicle", 0.18),
        ("Meals / Per Diem", "Meet meals and per diem", "Team Travel", 0.13),
        ("Competition Operations", "Meet entry fees", "Meet Hosts", 0.10),
        ("Equipment & Supplies", "Competition footwear support", "Running Specialty Vendor", 0.10),
        ("Equipment & Supplies", "Uniforms and training apparel", "Nike / BSN Sports", 0.08),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.06),
        ("Technology / Software", "Timing / performance software", "Timing Vendor", 0.05),
        ("Other Program Operations", "Hydration and recovery supplies", "Performance Health", 0.04),
        ("Other Program Operations", "Program operations contingency", "Program Operations", 0.04),
    ],
    "baseball": [
        ("Travel", "Conference hotel blocks", "Marriott / Hilton", 0.17),
        ("Travel", "Team transportation", "Charter Bus Vendor", 0.13),
        ("Meals / Per Diem", "Road meals and per diem", "Team Travel", 0.10),
        ("Competition Operations", "Officials and game operations", "CCAA / Officials", 0.11),
        ("Equipment & Supplies", "Baseballs and competition equipment", "Rawlings", 0.13),
        ("Equipment & Supplies", "Uniforms and protective equipment", "Rawlings / BSN Sports", 0.10),
        ("Facilities / Rentals", "Field maintenance and game prep", "Field Operations", 0.09),
        ("Technology / Software", "Video / analytics platform", "Hudl / Rapsodo", 0.06),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.06),
        ("Other Program Operations", "Training and medical supplies", "Performance Health", 0.05),
    ],
    "softball": [
        ("Travel", "Conference hotel blocks", "Marriott / Hilton", 0.17),
        ("Travel", "Team transportation", "Charter Bus Vendor", 0.13),
        ("Meals / Per Diem", "Road meals and per diem", "Team Travel", 0.10),
        ("Competition Operations", "Officials and game operations", "CCAA / Officials", 0.11),
        ("Equipment & Supplies", "Softballs and competition equipment", "Rawlings", 0.13),
        ("Equipment & Supplies", "Uniforms and protective equipment", "Rawlings / BSN Sports", 0.10),
        ("Facilities / Rentals", "Field maintenance and game prep", "Field Operations", 0.09),
        ("Technology / Software", "Video / analytics platform", "Hudl / Rapsodo", 0.06),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.06),
        ("Other Program Operations", "Training and medical supplies", "Performance Health", 0.05),
    ],
    "volleyball": [
        ("Travel", "Away-match hotel blocks", "Marriott / Hilton", 0.18),
        ("Travel", "Team transportation", "Charter Bus Vendor", 0.14),
        ("Meals / Per Diem", "Road meals and per diem", "Team Travel", 0.11),
        ("Competition Operations", "Officials and match operations", "CCAA / Officials", 0.11),
        ("Equipment & Supplies", "Uniforms and competition apparel", "Nike / BSN Sports", 0.11),
        ("Equipment & Supplies", "Volleyballs and training equipment", "Molten / BSN Sports", 0.09),
        ("Technology / Software", "Video / scouting platform", "Hudl / Volleymetrics", 0.08),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.07),
        ("Facilities / Rentals", "Event and facility support", "Campus Operations", 0.06),
        ("Other Program Operations", "Recovery and medical supplies", "Performance Health", 0.05),
    ],
    "golf": [
        ("Travel", "Tournament hotel blocks", "Marriott / Hilton", 0.22),
        ("Travel", "Tournament transportation", "Rental Vehicle Vendor", 0.15),
        ("Meals / Per Diem", "Tournament meals and per diem", "Team Travel", 0.11),
        ("Competition Operations", "Tournament entry fees", "Tournament Hosts", 0.13),
        ("Equipment & Supplies", "Golf balls and competition supplies", "Titleist / Team Vendor", 0.10),
        ("Equipment & Supplies", "Apparel and bags", "Team Golf Vendor", 0.08),
        ("Facilities / Rentals", "Practice / course access", "Local Golf Facilities", 0.08),
        ("Recruiting", "Recruiting travel and events", "Recruiting Travel", 0.05),
        ("Technology / Software", "Tournament analytics platform", "Golfstat / Analytics Vendor", 0.04),
        ("Other Program Operations", "Program operations contingency", "Program Operations", 0.04),
    ],
    "default": [
        ("Travel", "Travel and lodging obligation", "Travel Vendor", 0.18),
        ("Travel", "Transportation obligation", "Transportation Vendor", 0.13),
        ("Meals / Per Diem", "Meals and per diem", "Team Travel", 0.10),
        ("Competition Operations", "Competition operations", "Operations Vendor", 0.10),
        ("Equipment & Supplies", "Competition equipment", "Equipment Vendor", 0.12),
        ("Equipment & Supplies", "Uniforms and supplies", "Team Vendor", 0.10),
        ("Technology / Software", "Program technology", "Software Vendor", 0.07),
        ("Recruiting", "Recruiting travel", "Recruiting Travel", 0.07),
        ("Facilities / Rentals", "Facility operations", "Campus Operations", 0.07),
        ("Other Program Operations", "Other approved operating needs", "Program Operations", 0.06),
    ],
}


def _po_template_for_program(program_name):
    name = str(program_name).lower()
    for key in ["cross country", "basketball", "soccer", "baseball", "softball", "volleyball", "golf"]:
        if key in name:
            return PO_TEMPLATES[key]
    return PO_TEMPLATES["default"]


def _po_months_for_program(program_name):
    name = str(program_name).lower()
    if "basketball" in name:
        return ["2027-10-22", "2027-11-12", "2027-11-28", "2027-12-10", "2028-01-15", "2028-01-29", "2028-02-12", "2028-02-26", "2028-03-08", "2028-03-20"]
    if any(k in name for k in ["soccer", "volleyball", "cross country"]):
        return ["2027-10-12", "2027-10-20", "2027-10-28", "2027-11-05", "2027-11-12", "2027-11-19", "2027-11-26", "2028-02-15", "2028-03-15", "2028-04-15"]
    if any(k in name for k in ["baseball", "softball"]):
        return ["2027-11-20", "2027-12-15", "2028-01-12", "2028-01-26", "2028-02-10", "2028-02-24", "2028-03-12", "2028-04-10", "2028-05-05", "2028-05-20"]
    if "golf" in name:
        return ["2027-10-15", "2027-11-10", "2027-11-24", "2028-02-12", "2028-02-26", "2028-03-12", "2028-03-26", "2028-04-12", "2028-04-26", "2028-05-10"]
    return ["2027-10-20", "2027-11-15", "2027-12-15", "2028-01-15", "2028-02-15", "2028-03-15", "2028-04-15", "2028-05-01", "2028-05-20", "2028-06-05"]


def approved_purchase_orders_df():
    """Build simulated open POs that reconcile to KORBI's current committed balance."""
    rows = []
    decisions = current_decision_df()
    approved_decisions = pd.DataFrame()
    if not decisions.empty and "manager_decision" in decisions.columns:
        approved_decisions = decisions[
            decisions["manager_decision"].astype(str).str.upper() == "APPROVE"
        ].copy()

    programs = []
    if not triage_df.empty and "program_name" in triage_df.columns:
        programs = sorted(triage_df["program_name"].dropna().astype(str).unique())

    po_counter = 1001
    for program in programs:
        metrics = program_metrics(program)
        if not metrics:
            continue
        total_committed = max(safe_float(metrics.get("committed")), 0.0)

        live = pd.DataFrame()
        if not approved_decisions.empty and "program_name" in approved_decisions.columns:
            live = approved_decisions[
                approved_decisions["program_name"].astype(str) == str(program)
            ].copy()
        live_total = pd.to_numeric(live.get("amount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum() if not live.empty else 0.0
        seeded_total = max(total_committed - live_total, 0.0)

        template = _po_template_for_program(program)
        dates = _po_months_for_program(program)
        allocated = 0.0
        for i, (category, desc, vendor, weight) in enumerate(template):
            amount = round(seeded_total * weight, 2)
            if i == len(template) - 1:
                amount = round(seeded_total - allocated, 2)
            allocated += amount
            if amount <= 0:
                continue
            rows.append({
                "PO #": f"PO-{po_counter}",
                "Request #": f"SIM-{program[:3].upper()}-{i+1:02d}",
                "Program": program,
                "Vendor": vendor,
                "Description": desc,
                "Category": category,
                "Approved Amount": amount,
                "Approval Date": "2027-09-28",
                "Expected Invoice / Delivery": dates[i % len(dates)],
                "Expected Posting Month": pd.Timestamp(dates[i % len(dates)]).strftime("%b %Y"),
                "PO Status": "OPEN",
                "Amount Invoiced": 0.0,
                "Remaining PO Balance": amount,
                "Source": "Simulated Open PO",
            })
            po_counter += 1

        if not live.empty:
            for _, rec in live.iterrows():
                amt = safe_float(rec.get("amount"))
                if amt <= 0:
                    continue
                rows.append({
                    "PO #": f"PO-{po_counter}",
                    "Request #": str(rec.get("request_id", "")),
                    "Program": program,
                    "Vendor": "Pending vendor assignment",
                    "Description": str(rec.get("description", "Approved purchase request")),
                    "Category": str(rec.get("category_code", "Other Program Operations")),
                    "Approved Amount": amt,
                    "Approval Date": str(rec.get("review_date", SIMULATION_DATE))[:10],
                    "Expected Invoice / Delivery": "2027-11-15",
                    "Expected Posting Month": "Nov 2027",
                    "PO Status": "OPEN",
                    "Amount Invoiced": 0.0,
                    "Remaining PO Balance": amt,
                    "Source": "Live KORBI Approval",
                })
                po_counter += 1

    # Allocate any department-level committed balance not assigned to sports.
    dept = department_financial_summary()
    program_committed = sum(safe_float(program_metrics(p).get("committed")) for p in programs if program_metrics(p))
    shared_committed = max(safe_float(dept.get("committed")) - program_committed, 0.0)
    if shared_committed > 0:
        admin_items = [
            ("Athletics Administration", "Department software and licenses", "Technology Vendor", .16, "2027-11-15"),
            ("Athletics Administration", "Sports medicine shared supplies", "Performance Health", .14, "2027-11-30"),
            ("Athletics Administration", "Game operations staffing / services", "Event Operations", .16, "2027-12-15"),
            ("Athletics Administration", "Facilities and equipment maintenance", "Campus Facilities", .15, "2028-01-15"),
            ("Athletics Administration", "Department travel / vehicle services", "Travel Vendor", .11, "2028-02-15"),
            ("Athletics Administration", "Compliance / membership obligations", "NCAA / CCAA", .10, "2028-03-15"),
            ("Athletics Administration", "Marketing and communications services", "Creative Services", .09, "2028-04-15"),
            ("Athletics Administration", "Shared operational contingency commitments", "Department Operations", .09, "2028-05-15"),
        ]
        allocated = 0.0
        for i, (program, desc, vendor, wt, date) in enumerate(admin_items):
            amount = round(shared_committed * wt, 2)
            if i == len(admin_items)-1:
                amount = round(shared_committed - allocated, 2)
            allocated += amount
            rows.append({
                "PO #": f"PO-{po_counter}", "Request #": f"SIM-ADM-{i+1:02d}", "Program": program,
                "Vendor": vendor, "Description": desc, "Category": "Shared / Department Costs",
                "Approved Amount": amount, "Approval Date": "2027-09-28", "Expected Invoice / Delivery": date,
                "Expected Posting Month": pd.Timestamp(date).strftime("%b %Y"), "PO Status": "OPEN",
                "Amount Invoiced": 0.0, "Remaining PO Balance": amount, "Source": "Simulated Open PO",
            })
            po_counter += 1

    return pd.DataFrame(rows)


DENIED_REQUEST_SEED = [
    ("Men's Soccer", "Second portable recovery unit package", 6800, "Current-year operating flexibility is insufficient for a second recovery package."),
    ("Women's Soccer", "Premium GPS upgrade package", 11200, "Existing tracking solution meets current competition requirements."),
    ("Men's Basketball", "Locker room entertainment upgrade", 14500, "Nonessential enhancement does not justify reducing competition and travel capacity."),
    ("Women's Basketball", "Additional travel apparel package", 7200, "Current apparel allocation is sufficient for the season."),
    ("Baseball", "Premium dugout technology display", 12800, "Technology enhancement is not required for competition readiness."),
    ("Softball", "Secondary pitching technology package", 9800, "Existing equipment remains serviceable; higher-priority travel costs retained."),
    ("Men's Cross Country", "Optional out-of-region invitational travel", 8400, "Additional competition travel would exceed the approved travel strategy."),
    ("Women's Cross Country", "Optional out-of-region invitational travel", 8400, "Additional competition travel would exceed the approved travel strategy."),
    ("Women's Volleyball", "Premium practice analytics package", 7600, "Current video platform is adequate for FY 2027-28."),
    ("Men's Golf", "Additional spring invitational", 9200, "Tournament schedule is already sufficient and travel capacity is limited."),
]


def denied_requests_df():
    rows = []
    for i, (program, desc, amount, reason) in enumerate(DENIED_REQUEST_SEED, start=1):
        rows.append({
            "Request #": f"DEN-{i:03d}",
            "Program": program,
            "Description": desc,
            "Amount": amount,
            "Denial Date": "2027-10-01",
            "Reason Denied": reason,
            "Reviewer": "Athletics Business Office",
            "Resubmittable": "Yes - if funding or operating need changes",
            "Future Budget Consideration": "No - unless revalidated",
            "Source": "Simulated Denial",
        })

    decisions = current_decision_df()
    if not decisions.empty and "manager_decision" in decisions.columns:
        denied = decisions[decisions["manager_decision"].astype(str).str.upper() == "DENY"].copy()
        for _, rec in denied.iterrows():
            rows.append({
                "Request #": str(rec.get("request_id", "")),
                "Program": str(rec.get("program_name", "")),
                "Description": str(rec.get("description", "")),
                "Amount": safe_float(rec.get("amount")),
                "Denial Date": str(rec.get("review_date", SIMULATION_DATE))[:10],
                "Reason Denied": str(rec.get("decision_rationale", rec.get("manager_notes", ""))),
                "Reviewer": str(rec.get("reviewed_by", "")),
                "Resubmittable": "Yes - if conditions materially change",
                "Future Budget Consideration": "No - move to Deferred if it should be tracked for next year",
                "Source": "Live KORBI Decision",
            })
    return pd.DataFrame(rows)


def _program_category_weights(program_name):
    """
    Simulated operating-budget mix by sport. These are planning allocations, not actual
    Sonoma State historical category budgets. They always total 100%.
    """
    name = str(program_name).lower()

    # Travel, Equipment/Supplies, Competition Ops, Recruiting, Facilities/Rentals,
    # Technology/Software, Meals/Per Diem, Other Program Ops
    default = [0.29, 0.13, 0.12, 0.06, 0.10, 0.05, 0.12, 0.13]

    if "golf" in name:
        return [0.36, 0.14, 0.12, 0.07, 0.05, 0.04, 0.12, 0.10]
    if "basketball" in name:
        return [0.27, 0.12, 0.15, 0.06, 0.08, 0.06, 0.13, 0.13]
    if "soccer" in name:
        return [0.30, 0.13, 0.12, 0.06, 0.10, 0.04, 0.12, 0.13]
    if "baseball" in name or "softball" in name:
        return [0.29, 0.16, 0.13, 0.06, 0.11, 0.03, 0.10, 0.12]
    if "volleyball" in name:
        return [0.28, 0.12, 0.15, 0.06, 0.08, 0.05, 0.13, 0.13]
    if "track" in name or "cross country" in name or "xc" in name:
        return [0.28, 0.11, 0.12, 0.05, 0.13, 0.03, 0.12, 0.16]
    return default


def _normalized_weighted_distribution(total, base_weights, spend_factors):
    raw = [max(w * f, 0) for w, f in zip(base_weights, spend_factors)]
    denom = sum(raw)
    if total <= 0 or denom <= 0:
        return [0.0 for _ in raw]
    return [total * x / denom for x in raw]


def program_budget_breakdown(program_name):
    """
    Build a connected simulated operating-budget detail for one sport. The category rows
    reconcile exactly to program_metrics(), so the Sport Budgets page and Executive
    Dashboard always report the same overall health and year-end position.
    """
    metrics = program_metrics(program_name)
    if not metrics:
        return pd.DataFrame()

    categories = [
        "Travel",
        "Equipment & Supplies",
        "Competition Operations",
        "Recruiting",
        "Facilities / Rentals",
        "Technology / Software",
        "Meals / Per Diem",
        "Other Program Operations",
    ]
    weights = _program_category_weights(program_name)

    annual_by_cat = [metrics["annual"] * w for w in weights]

    # Q1 actuals are intentionally front-loaded toward equipment, competition setup,
    # facilities, and travel as teams launch the year.
    actual_factors = [1.05, 1.30, 1.18, 0.72, 1.15, 0.95, 1.00, 0.86]
    actual_by_cat = _normalized_weighted_distribution(
        metrics["actual"], weights, actual_factors
    )

    # Commitments are weighted toward travel, competition operations, facilities and meals.
    committed_factors = [1.32, 0.82, 1.20, 0.68, 1.08, 0.82, 1.18, 0.72]
    committed_by_cat = _normalized_weighted_distribution(
        metrics["committed"], weights, committed_factors
    )

    # Remaining forecast covers the balance of expected annual activity.
    forecast_factors = [1.08, 0.90, 1.00, 1.05, 0.92, 1.02, 1.08, 0.98]
    forecast_by_cat = _normalized_weighted_distribution(
        metrics["remaining_forecast"], weights, forecast_factors
    )

    rows = []
    for i, category in enumerate(categories):
        projected = actual_by_cat[i] + committed_by_cat[i] + forecast_by_cat[i]
        remaining = annual_by_cat[i] - projected
        util = (projected / annual_by_cat[i] * 100) if annual_by_cat[i] else 0.0
        status, _ = program_health(util)
        rows.append({
            "Category": category,
            "Annual Budget": annual_by_cat[i],
            "Q1 Actual": actual_by_cat[i],
            "Committed": committed_by_cat[i],
            "Remaining Forecast": forecast_by_cat[i],
            "Projected Year-End": projected,
            "Projected Remaining": remaining,
            "Utilization": util,
            "Health": status,
        })

    df = pd.DataFrame(rows)

    # Numerical cleanup: force category totals to equal the authoritative program totals
    # exactly after floating-point allocation.
    for col, target in [
        ("Annual Budget", metrics["annual"]),
        ("Q1 Actual", metrics["actual"]),
        ("Committed", metrics["committed"]),
        ("Remaining Forecast", metrics["remaining_forecast"]),
        ("Projected Year-End", metrics["projected"]),
        ("Projected Remaining", metrics["remaining"]),
    ]:
        if not df.empty:
            df.loc[df.index[-1], col] += target - df[col].sum()

    df["Utilization"] = df.apply(
        lambda r: (safe_float(r["Projected Year-End"]) / safe_float(r["Annual Budget"]) * 100)
        if safe_float(r["Annual Budget"]) else 0.0,
        axis=1,
    )
    df["Health"] = df["Utilization"].apply(lambda x: program_health(x)[0])
    return df



def _department_source_totals():
    result = {"annual": 0.0, "actual": 0.0, "committed": 0.0, "projected": 0.0}
    if department_df.empty:
        return result

    mapping = {
        "annual": ["annual_budget", "budget", "annual_plan"],
        "actual": ["q1_actual", "q1_actuals", "actual", "actuals"],
        "committed": ["open_commitments", "open_pos", "committed", "commitments"],
        "projected": ["projected_year_end", "baseline_projected", "projected"],
    }

    for key, candidates in mapping.items():
        col = first_existing_column(department_df, candidates)
        if col:
            result[key] = pd.to_numeric(department_df[col], errors="coerce").fillna(0).sum()

    return result


def shared_department_cost_breakdown(shared_budget):
    """Simulated shared athletics cost allocation. Categories reconcile exactly to shared budget."""
    categories = [
        ("Athletics Administration & Department Staff", 0.30),
        ("Facilities / Game Operations", 0.18),
        ("Sports Medicine / Athletic Training", 0.12),
        ("Strength & Conditioning", 0.08),
        ("Compliance / Academic Support", 0.08),
        ("Communications / Marketing", 0.06),
        ("Technology / Software", 0.05),
        ("Department Travel / Vehicles", 0.04),
        ("Insurance / Memberships / NCAA / CCAA", 0.04),
        ("Shared Equipment / Supplies / Contingency", 0.05),
    ]
    rows = []
    running = 0.0
    for idx, (category, weight) in enumerate(categories):
        if idx == len(categories) - 1:
            amount = safe_float(shared_budget) - running
        else:
            amount = safe_float(shared_budget) * weight
            running += amount
        rows.append({"Shared Cost Category": category, "Annual Budget": amount})
    return pd.DataFrame(rows)


def program_budget_reconciliation():
    programs = []
    if not triage_df.empty and "program_name" in triage_df.columns:
        programs = sorted(triage_df["program_name"].dropna().astype(str).unique())

    sport_budget = 0.0
    for program in programs:
        base = _base_program_metrics(program)
        if base:
            sport_budget += base["annual"]

    source = _department_source_totals()
    source_athletics_budget = source["annual"]

    # Department annual plan is authoritative when it covers the sport budgets.
    # If source data is incomplete, KORBI will never create a negative shared-cost bucket.
    total_athletics_budget = max(source_athletics_budget, sport_budget)
    shared_budget = max(total_athletics_budget - sport_budget, 0)
    reconciliation_difference = total_athletics_budget - sport_budget - shared_budget

    return {
        "sport_budget": sport_budget,
        "shared_budget": shared_budget,
        "total_athletics_budget": total_athletics_budget,
        "reconciliation_difference": reconciliation_difference,
        "source_athletics_budget": source_athletics_budget,
        "program_count": len(programs),
    }


def department_financial_summary():
    source = _department_source_totals()
    recon = program_budget_reconciliation()

    programs = []
    if not triage_df.empty and "program_name" in triage_df.columns:
        programs = sorted(triage_df["program_name"].dropna().astype(str).unique())

    base_sport = {"actual": 0.0, "committed": 0.0, "projected": 0.0}
    current_sport = {"actual": 0.0, "committed": 0.0, "projected": 0.0}

    for program in programs:
        base = _base_program_metrics(program)
        current = program_metrics(program)
        if base:
            for key in base_sport:
                base_sport[key] += base[key]
        if current:
            for key in current_sport:
                current_sport[key] += current[key]

    # Anything in the department source that is not assigned to a sport is treated as shared/admin cost.
    shared_actual = max(source["actual"] - base_sport["actual"], 0)
    shared_committed = max(source["committed"] - base_sport["committed"], 0)
    shared_projected = max(source["projected"] - base_sport["projected"], 0)

    actual = current_sport["actual"] + shared_actual
    committed = current_sport["committed"] + shared_committed
    projected = current_sport["projected"] + shared_projected
    projected = max(projected, actual + committed)

    annual = recon["total_athletics_budget"]
    remaining_forecast = max(projected - actual - committed, 0)
    variance = annual - projected
    approved_adjustment = approved_decision_adjustments()

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "approved_decision_adjustment": approved_adjustment,
        "remaining_forecast": remaining_forecast,
        "projected": projected,
        "variance": variance,
        "shared_actual": shared_actual,
        "shared_committed": shared_committed,
        "shared_projected": shared_projected,
        **recon,
    }


def funding_summary():
    result = {
        "modeled_university_support": 0.0,
        "student_fees": 0.0,
        "external_revenue": 0.0,
        "one_time_rebuild": 0.0,
    }

    if funding_df.empty:
        return result

    amount_col = first_existing_column(funding_df, ["amount", "funding_amount", "value"])
    category_col = first_existing_column(funding_df, ["funding_category", "category", "revenue_category"])
    model_col = first_existing_column(funding_df, ["model_type", "model"])

    if not amount_col or not category_col:
        return result

    temp = funding_df.copy()
    temp["_amount"] = pd.to_numeric(temp[amount_col], errors="coerce").fillna(0)

    if model_col:
        one_time_mask = temp[model_col].astype(str).str.contains(
            "ONE_TIME_REBUILD", case=False, na=False
        )
        result["one_time_rebuild"] = temp.loc[one_time_mask, "_amount"].sum()
        recurring = temp.loc[~one_time_mask].copy()
    else:
        recurring = temp.copy()

    categories = recurring[category_col].astype(str)

    result["modeled_university_support"] = recurring.loc[
        categories.str.contains(
            "INSTITUTIONAL_SUPPORT|UNIVERSITY_SUPPORT", case=False, na=False, regex=True
        ),
        "_amount",
    ].sum()

    result["student_fees"] = recurring.loc[
        categories.str.contains(
            "STUDENT_FEES|STUDENT FEE", case=False, na=False, regex=True
        ),
        "_amount",
    ].sum()

    result["external_revenue"] = recurring.loc[
        categories.str.contains(
            (
                "FUNDRAISING|DONATION|DONOR|SPONSOR|TICKET|CAMP|CLINIC|"
                "MERCH|LICENS|NCAA|CONFERENCE|OTHER_REVENUE|EXTERNAL|CORPORATE|PARTNERSHIP"
            ),
            case=False,
            na=False,
            regex=True,
        ),
        "_amount",
    ].sum()

    return result


def university_support_projection():
    financial = department_financial_summary()
    funding = funding_summary()

    projected_expenses = financial["projected"]
    before_external = max(projected_expenses - funding["student_fees"], 0)
    required_support = max(before_external - funding["external_revenue"], 0)
    external_reduction = before_external - required_support

    return {
        **financial,
        **funding,
        "support_before_external": before_external,
        "required_support": required_support,
        "external_reduction": external_reduction,
    }


def request_status_table(program_name=None):
    if triage_df.empty:
        return pd.DataFrame()

    view = triage_df.copy()

    if program_name and program_name != "All Programs" and "program_name" in view.columns:
        view = view[view["program_name"].astype(str) == str(program_name)].copy()

    decisions = current_decision_df()
    if (
        not decisions.empty
        and "request_id" in decisions.columns
        and "request_id" in view.columns
    ):
        decision_cols = [
            c for c in [
                "request_id", "manager_decision", "review_date", "reviewed_by",
                "manager_notes", "requestor_name", "decision_rationale",
                "requestor_email_response"
            ]
            if c in decisions.columns
        ]
        view = view.merge(
            decisions[decision_cols],
            on="request_id",
            how="left",
            suffixes=("", "_decision"),
        )

    def classify_status(row):
        decision = str(row.get("manager_decision", "")).upper().strip()
        if decision == "APPROVE":
            return "APPROVED"
        if decision == "DENY":
            return "DENIED"
        return "OPEN"

    def classify_type(row):
        allocation_fields = [
            "request_type", "budget_type", "allocation_status", "funding_status",
            "planned_status", "plan_status", "planned", "allocated"
        ]
        allocation_text = " ".join(str(row.get(field, "")) for field in allocation_fields).upper()
        if any(word in allocation_text for word in ["ALLOCATED", "PLANNED", "BUDGETED", "TRUE", "YES"]):
            return "ALLOCATED"
        return "UNPLANNED"

    view["request_status"] = view.apply(classify_status, axis=1)
    view["request_type"] = view.apply(classify_type, axis=1)
    return view


def _scope_financial_totals(program_name=None):
    if program_name and program_name != "Entire Athletics":
        metrics = program_metrics(program_name)
        if not metrics:
            return {"annual": 0.0, "actual": 0.0, "committed": 0.0, "remaining_forecast": 0.0, "projected": 0.0}
        return metrics
    return department_financial_summary()


def _monthly_source_values(df, program_name, amount_candidates, date_candidates, committed_only=None):
    values = {}
    if df.empty:
        return values

    date_col = first_existing_column(df, date_candidates)
    amount_col = first_existing_column(df, amount_candidates)
    program_col = first_existing_column(df, ["program_name", "program", "sport", "team"])
    type_col = first_existing_column(df, ["transaction_type", "type", "status"])

    if not date_col or not amount_col:
        return values

    temp = df.copy()
    if program_name and program_name != "Entire Athletics":
        if not program_col:
            return values
        temp = temp[temp[program_col].astype(str) == str(program_name)].copy()

    if committed_only is True and not type_col:
        return values

    temp["_date"] = pd.to_datetime(temp[date_col], errors="coerce")
    temp["_amount"] = pd.to_numeric(temp[amount_col], errors="coerce").fillna(0)
    temp = temp[temp["_date"].notna()].copy()

    if type_col and committed_only is not None:
        committed_mask = temp[type_col].astype(str).str.contains(
            "PO|OPEN|COMMIT|APPROV", case=False, na=False, regex=True
        )
        temp = temp[committed_mask if committed_only else ~committed_mask].copy()

    temp["month_date"] = temp["_date"].dt.to_period("M").dt.to_timestamp()
    return temp.groupby("month_date")["_amount"].sum().to_dict()


def _scaled_distribution(target_total, source_by_month, allowed_months, weights):
    result = {m: 0.0 for m in allowed_months}
    target_total = max(safe_float(target_total), 0)
    if target_total <= 0 or not allowed_months:
        return result

    positive_source = {m: max(safe_float(source_by_month.get(m, 0)), 0) for m in allowed_months}
    source_total = sum(positive_source.values())

    if source_total > 0:
        scale = target_total / source_total
        for month in allowed_months:
            result[month] = positive_source[month] * scale
        return result

    active_weights = [max(safe_float(weights.get(m, 0)), 0) for m in allowed_months]
    weight_total = sum(active_weights)
    if weight_total <= 0:
        equal = target_total / len(allowed_months)
        return {m: equal for m in allowed_months}

    return {
        m: target_total * (max(safe_float(weights.get(m, 0)), 0) / weight_total)
        for m in allowed_months
    }


def _sport_monthly_plan_weights(program_name=None):
    """
    Simulated FY seasonality profile used to time annual operating budgets by sport.
    The weights always total 100%, so changing timing never changes the annual budget.
    """
    # Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun
    generic = [0.06, 0.08, 0.09, 0.09, 0.08, 0.06, 0.08, 0.10, 0.10, 0.09, 0.08, 0.09]
    if not program_name or str(program_name).strip().lower() in {"entire athletics", "athletics"}:
        return generic

    name = str(program_name).lower()

    # Fall championship sports: preseason/startup in Jul-Aug, competition Sep-Nov.
    if "cross country" in name or "xc" in name:
        return [0.08, 0.16, 0.20, 0.20, 0.14, 0.04, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03]
    if "soccer" in name:
        return [0.08, 0.17, 0.20, 0.19, 0.13, 0.04, 0.03, 0.03, 0.03, 0.03, 0.04, 0.03]
    if "volleyball" in name:
        return [0.07, 0.16, 0.20, 0.20, 0.14, 0.04, 0.03, 0.03, 0.03, 0.03, 0.04, 0.03]

    # Basketball ramps in Oct and carries substantial travel/game costs Nov-Mar.
    if "basketball" in name:
        return [0.03, 0.04, 0.06, 0.10, 0.14, 0.13, 0.14, 0.14, 0.11, 0.04, 0.04, 0.03]

    # Spring championship sports: preseason ramp in Jan, peak travel/competition Feb-May.
    if "baseball" in name:
        return [0.03, 0.03, 0.04, 0.04, 0.04, 0.04, 0.10, 0.15, 0.16, 0.16, 0.14, 0.07]
    if "softball" in name:
        return [0.03, 0.03, 0.04, 0.04, 0.04, 0.04, 0.10, 0.15, 0.16, 0.16, 0.14, 0.07]

    # Golf has meaningful fall and spring competitive periods.
    if "golf" in name:
        return [0.04, 0.07, 0.12, 0.12, 0.08, 0.04, 0.06, 0.10, 0.12, 0.11, 0.09, 0.05]

    # Track & field is concentrated in the indoor/outdoor spring cycle.
    if "track" in name:
        return [0.03, 0.03, 0.04, 0.04, 0.05, 0.06, 0.10, 0.13, 0.15, 0.16, 0.14, 0.07]

    return generic


def monthly_financial_outlook(program_name=None):
    """
    Connected FY 2027-28 simulation as of Oct. 1, 2027.

    Jul-Sep are completed Q1 months. Oct is the current month. Nov-Jun are forecast.
    The monthly table always reconciles back to the exact same annual/actual/committed/
    forecast totals used by Sport Budgets and the Executive Dashboard.
    """
    months = list(pd.date_range("2027-07-01", "2028-06-01", freq="MS"))
    simulation_month = pd.Timestamp(SIMULATION_DATE).to_period("M").to_timestamp()
    q1_months = [m for m in months if m < simulation_month]
    future_months = [m for m in months if m >= simulation_month]

    totals = _scope_financial_totals(program_name)
    annual = safe_float(totals.get("annual"))
    actual_total = safe_float(totals.get("actual"))
    committed_total = safe_float(totals.get("committed"))
    remaining_forecast_total = max(
        safe_float(totals.get("projected")) - actual_total - committed_total,
        0,
    )

    # Sport-specific seasonality: annual totals stay fixed while monthly timing follows
    # the program's competitive calendar. Entire Athletics uses a blended department profile.
    plan_weight_values = _sport_monthly_plan_weights(program_name)
    plan_weights = {m: w for m, w in zip(months, plan_weight_values)}
    monthly_plan = {m: annual * plan_weights[m] for m in months}

    ledger_actual_source = _monthly_source_values(
        ledger_df,
        program_name,
        ["amount", "transaction_amount", "expense_amount", "actual_amount"],
        ["transaction_date", "posting_date", "expense_date", "date"],
        committed_only=False,
    )
    ledger_commitment_source = _monthly_source_values(
        ledger_df,
        program_name,
        ["amount", "transaction_amount", "expense_amount", "actual_amount"],
        ["transaction_date", "posting_date", "expense_date", "date"],
        committed_only=True,
    )
    future_source = _monthly_source_values(
        future_df,
        program_name,
        ["amount", "expected_amount", "forecast_amount", "expense_amount"],
        ["expense_date", "expected_date", "scheduled_date", "date", "transaction_date"],
        committed_only=None,
    )

    # Q1 is complete in this simulation. Use a realistic executed-spend profile
    # that reconciles exactly to the same Q1 actual total used everywhere else.
    # Department-wide this produces: Jul $356,400; Aug $470,750; Sep $528,184
    # when Q1 actuals total $1,355,334. Sport views use the same Q1 proportions,
    # so every page remains tied to one connected financial model.
    if not program_name or str(program_name).strip().lower() in {"entire athletics", "athletics"}:
        q1_actual_profile = {
            pd.Timestamp("2027-07-01"): 356400 / 1355334,
            pd.Timestamp("2027-08-01"): 470750 / 1355334,
            pd.Timestamp("2027-09-01"): 528184 / 1355334,
        }
    else:
        q1_weight_total = sum(plan_weights.get(m, 0.0) for m in q1_months)
        if q1_weight_total > 0:
            q1_actual_profile = {m: plan_weights.get(m, 0.0) / q1_weight_total for m in q1_months}
        else:
            q1_actual_profile = {m: 1 / len(q1_months) for m in q1_months}

    actual_by_month = {
        month: actual_total * q1_actual_profile.get(month, 0.0)
        for month in q1_months
    }

    # Open commitments at the end of Q1 belong in Oct-Jun. If a vendor invoice slipped out
    # of Q1, the obligation is carried forward instead of disappearing from the model.
    commitment_weights = dict(plan_weights)
    if simulation_month in commitment_weights:
        commitment_weights[simulation_month] *= 1.45
    committed_by_month = _scaled_distribution(
        committed_total,
        ledger_commitment_source,
        future_months,
        commitment_weights,
    )

    # Forecast rule for months that have not happened yet:
    # Monthly Plan = Committed + Remaining Forecast.
    # This keeps future months fully planned unless there is a specific reason to
    # project an overage/underrun. The current month absorbs any remaining annual
    # forecast needed to keep the monthly model tied to the same year-end projection.
    forecast_by_month = {m: 0.0 for m in future_months}

    future_only_months = [m for m in future_months if m > simulation_month]
    for month in future_only_months:
        plan = monthly_plan.get(month, 0.0)
        committed = committed_by_month.get(month, 0.0)
        forecast_by_month[month] = max(plan - committed, 0.0)

    future_forecast_required = sum(
        forecast_by_month.get(m, 0.0) for m in future_only_months
    )

    current_month_remainder = max(
        remaining_forecast_total - future_forecast_required,
        0.0,
    )

    if simulation_month in forecast_by_month:
        forecast_by_month[simulation_month] = current_month_remainder

    rows = []
    for month in months:
        actual = actual_by_month.get(month, 0.0)
        committed = committed_by_month.get(month, 0.0)
        forecast = forecast_by_month.get(month, 0.0)
        projected_month_end = actual + committed + forecast
        plan = monthly_plan.get(month, 0.0)
        variance = plan - projected_month_end

        if month < simulation_month:
            status = "EXECUTED"
        elif month == simulation_month:
            status = "CURRENT"
        else:
            status = "FORECAST"

        rows.append({
            "Month": month.strftime("%b %Y"),
            "Status": status,
            "Monthly Plan": plan,
            "Actual Posted": actual,
            "Committed": committed,
            "Remaining Forecast": forecast,
            "Projected Month-End": projected_month_end,
            "Variance to Plan": variance,
        })

    monthly = pd.DataFrame(rows)

    # Floating-point cleanup: force the final month to carry tiny rounding differences so
    # annual totals always tie exactly to the connected source totals.
    if not monthly.empty:
        corrections = {
            "Monthly Plan": annual - monthly["Monthly Plan"].sum(),
            "Actual Posted": actual_total - monthly["Actual Posted"].sum(),
            "Committed": committed_total - monthly["Committed"].sum(),
            "Remaining Forecast": remaining_forecast_total - monthly["Remaining Forecast"].sum(),
        }
        last_idx = monthly.index[-1]
        for col, correction in corrections.items():
            monthly.loc[last_idx, col] += correction
        monthly["Projected Month-End"] = (
            monthly["Actual Posted"] + monthly["Committed"] + monthly["Remaining Forecast"]
        )
        monthly["Variance to Plan"] = monthly["Monthly Plan"] - monthly["Projected Month-End"]

    return monthly


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def go_to_page(page_name):
    st.session_state["page_nav"] = page_name


if "page_nav" not in st.session_state:
    st.session_state["page_nav"] = "Home"


st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="ssu-mark">SONOMA STATE</div>
        <div class="ssu-sub">Seawolf Athletics · KORBI</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Executive Dashboard",
        "Monthly Financials",
        "Sport Budgets",
        "Purchase Requests",
        "Approved / Purchase Orders",
        "Denied Requests",
        "CSU Benchmarking",
        "Deferred & Future Needs",
        "Decision Log",
    ],
    label_visibility="collapsed",
    key="page_nav",
)

reviewer = st.sidebar.text_input(
    "Reviewer",
    value="Lonny Cunningham",
)

st.sidebar.caption(
    "Human approval remains required. KORBI provides decision support."
)

# Keep the landing page visually clean. Interior pages use a compact branded header.
if page != "Home":
    st.markdown(
        """
        <div class="korbi-header">
            <div class="korbi-title">KORBI</div>
            <div class="korbi-subtitle">Knowledge & Operations Resource for Business Intelligence</div>
            <div class="korbi-brandline">Sonoma State Athletics Business Operations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.markdown(
        textwrap.dedent(
            """
            <div class="hero">
                <div class="hero-inner">
                    <div class="hero-kicker">V7.6 Athletics Premium • Simulation Environment • Fall 2027 Restart Scenario</div>
                    <div class="hero-title">KORBI</div>
                    <div class="hero-sub">One operating picture for every program, every request, and every dollar.</div>
                    <div class="hero-body">
                        KORBI empowers coaches with financial context, aligns day-to-day decisions with department objectives,
                        standardizes operating procedures, and makes the year-round impact of budget changes clear before
                        decisions are made.
                    </div>
                </div>
            </div>

            <div class="value-grid">
                <div class="value-card">
                    <div class="num">EMPOWER</div>
                    <h3>Empower Coaches</h3>
                    <p>Give coaches visibility into spend, commitments, remaining flexibility, and the impact of new decisions.</p>
                </div>
                <div class="value-card">
                    <div class="num">ALIGN</div>
                    <h3>Align Business Objectives</h3>
                    <p>Connect individual team decisions to department priorities, forecasts, and institutional support.</p>
                </div>
                <div class="value-card">
                    <div class="num">STANDARDIZE</div>
                    <h3>Unify the Process</h3>
                    <p>Create one repeatable operating model for purchasing, travel, equipment, approvals, and financial review.</p>
                </div>
                <div class="value-card">
                    <div class="num">CLARIFY</div>
                    <h3>Clarify the Impact</h3>
                    <p>Show what saying yes today means for the financial flexibility a program may need later in the season.</p>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    launch1, launch2, launch3 = st.columns(3)

    with launch1:
        st.button(
            "Open Executive Dashboard",
            type="primary",
            width="stretch",
            on_click=go_to_page,
            args=("Executive Dashboard",),
        )

    with launch2:
        st.button(
            "View Sport Budgets",
            type="primary",
            width="stretch",
            on_click=go_to_page,
            args=("Sport Budgets",),
        )

    with launch3:
        st.button(
            "Review Purchase Requests",
            type="primary",
            width="stretch",
            on_click=go_to_page,
            args=("Purchase Requests",),
        )

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        st.markdown(
            textwrap.dedent(
                """
                <div class="landing-panel">
                    <div class="landing-eyebrow">The Problem KORBI Is Designed to Solve</div>
                    <h2>Restart athletics with limited staff—without losing control of the budget.</h2>
                    <p>
                        Sonoma State Athletics is preparing to restart intercollegiate sports in Fall 2027 with limited
                        staffing, significant operational work, and major startup needs. The gym and operating environment
                        must be rebuilt: equipment must be purchased, facilities prepared, travel and purchasing processes
                        established, coaches supported, vendors engaged, and budgets managed carefully from day one.
                        <br><br>
                        The challenge is not simply getting teams back on the field. It is doing so responsibly. Every
                        equipment purchase, travel request, vendor commitment, and operating decision affects the resources
                        available later in the year.
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            textwrap.dedent(
                """
                <div class="landing-panel">
                    <div class="landing-eyebrow">Operating Principle</div>
                    <h2>Not the department of “no.”</h2>
                    <p>
                        KORBI gives coaches and administrators enough information to understand tradeoffs, move faster,
                        and make informed decisions while preserving the financial flexibility needed to successfully finish
                        the season.
                        <br><br>
                        <strong style="color:#17365D">Build the program. Empower the coaches. Protect the budget.</strong>
                    </p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

    st.markdown("## What KORBI Can Do for Sonoma State")
    st.caption("One operating layer for Athletics")

    capability_cards = [
        (
            "Live Financial Picture",
            "See actual spend, approved commitments, open requests, future obligations, external revenue, and projected year-end position in one place.",
        ),
        (
            "Coach Budget Visibility",
            "Show each coach what has been spent, what is already committed, what remains, and how a request changes flexibility.",
        ),
        (
            "Forecast & University Support",
            "Continuously project year-end expenses and show how outside revenue can reduce the university support required.",
        ),
        (
            "Startup Readiness",
            "Track the equipment, supplies, facilities, travel, and operating work required to have teams ready for Fall 2027.",
        ),
        (
            "Standardized Requests",
            "Use the same request, review, approval, denial, and documentation process across every program.",
        ),
        (
            "Accountability",
            "Keep an audit trail of requests, management decisions, financial impact, approvals, denials, and remaining obligations.",
        ),
        (
            "Budget-Cycle Memory",
            "Carry deferred needs into the next fiscal-year planning cycle so equipment, travel, technology, and other unfunded requests are not forgotten.",
        ),
    ]

    for row_start in range(0, len(capability_cards), 3):
        cols = st.columns(3)
        for col, (title, body) in zip(cols, capability_cards[row_start:row_start + 3]):
            with col:
                card_html = (
                    '<div class="capability-card">'
                    f'<h3>{title}</h3>'
                    f'<p>{body}</p>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

elif page == "Executive Dashboard":

    section_title(
        "Executive Dashboard",
        "One connected financial picture for Q1 actuals, current commitments, remaining forecast, program budgets, and university support."
    )

    support = university_support_projection()
    recon = program_budget_reconciliation()

    st.markdown("## University Support Requirement")

    st.markdown(
        f"""
        <div class="support-card">
            <div class="support-kicker">Projected University Support Required</div>
            <div class="support-value">{money(support["required_support"])}</div>
            <div class="support-copy">
                External athletics revenue has reduced the modeled university requirement by
                <strong>{money(support["external_reduction"])}</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Projected Athletics Expenses", compact_money(support["projected"]))
    s2.metric("Student-Fee Support", compact_money(support["student_fees"]))
    s3.metric("External / Earned Revenue", compact_money(support["external_revenue"]))
    s4.metric("Net University Requirement", compact_money(support["required_support"]))

    st.caption(
        "External / earned revenue remains separate from university support. Each additional dollar of outside "
        "athletics revenue reduces the modeled university requirement dollar-for-dollar if expenses remain unchanged."
    )

    st.markdown("## Projected Year-End Position")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Q1 Actual Posted", compact_money(support["actual"]))
    f2.metric("Committed Obligations", compact_money(support["committed"]))
    f3.metric("Remaining Forecast", compact_money(support["remaining_forecast"]))
    f4.metric("Projected Year-End", compact_money(support["projected"]))

    st.caption(
        "Projected Year-End = Q1 Actual Posted + Committed Obligations + Remaining Forecast. "
        "When a commitment later posts as an actual, KORBI moves it between buckets rather than counting it twice."
    )

    if support["variance"] >= 0:
        st.markdown(
            f'<div class="neutral-note">KORBI currently projects Athletics to finish '
            f'<strong>{money(support["variance"])}</strong> favorable to the annual plan.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:#FCE8E6;color:#B42318;border:1px solid #F5C2BE;border-left:4px solid #B42318;'
            f'border-radius:8px;padding:14px 16px;margin:14px 0 22px;font-size:15px;font-weight:800;">'
            f'KORBI currently projects Athletics to finish {money(abs(support["variance"]))} over the annual plan.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("## Athletics Budget Reconciliation")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric(f"{recon['program_count']} Sport Budgets", money(recon["sport_budget"]))
    r2.metric("Shared / Department Costs", money(recon["shared_budget"]))
    r3.metric("Total Athletics Budget", money(recon["total_athletics_budget"]))
    r4.metric("Reconciliation Difference", money_zero(recon["reconciliation_difference"]))

    st.caption(
        "Sport Budgets + Shared / Department Costs = Total Athletics Budget. "
        "The reconciliation difference should remain $0."
    )

    with st.expander("Shared / Department Cost Detail"):
        shared_detail = shared_department_cost_breakdown(recon["shared_budget"])
        st.caption(
            "Simulated allocation of department-wide costs that are not assigned directly to one sport. "
            "These categories reconcile to the Shared / Department Costs total above."
        )
        st.dataframe(
            accounting_table(shared_detail, currency_cols=["Annual Budget"]),
            width="stretch",
            hide_index=True,
        )
        st.metric("Shared Cost Total", money(shared_detail["Annual Budget"].sum()))

    current_requests = request_status_table()
    decisions_now = current_decision_df()

    pending = 0
    high_risk = 0
    if not current_requests.empty:
        pending = int((current_requests["request_status"] == "OPEN").sum())
        if "financial_status" in current_requests.columns:
            high_risk = int(
                current_requests["financial_status"].astype(str).str.upper().isin(
                    ["HIGH RISK", "OVER BUDGET"]
                ).sum()
            )

    reviewed = len(decisions_now)

    st.markdown("## Management Workload")
    c1, c2, c3 = st.columns(3)
    c1.metric("Requests Awaiting Review", pending)
    c2.metric("Requests Reviewed", reviewed)
    c3.metric("High-Risk Requests", high_risk)

    st.markdown("## Program Budget Status — Restart Sports")

    cards = []
    if not triage_df.empty and "program_name" in triage_df.columns:
        for program_name in sorted(triage_df["program_name"].dropna().astype(str).unique()):
            metrics = program_metrics(program_name)
            if not metrics:
                continue

            util = metrics["utilization"]
            status, css = program_health(util)

            cards.append(
                f"""<div class=\"program-card {css}\">
                    <div class=\"sport\">{program_name}</div>
                    <div class=\"status\">{status}</div>
                    <div class=\"detail\">{util:.1f}% projected utilization | Remaining capacity: {money(metrics['remaining'])}</div>
                </div>"""
            )

    if cards:
        st.markdown(
            '<div class="program-grid">' + ''.join(cards) + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No sport-level budget positions are currently available.")

    st.markdown("## Department Financial Detail")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Annual Athletics Plan", money(support["annual"]))
    d2.metric("Q1 Actual Expenditures", money(support["actual"]))
    d3.metric("Projected Year-End", money(support["projected"]))
    d4.metric(
        "Projected Favorable Variance" if support["variance"] >= 0 else "Projected Unfavorable Variance",
        money(abs(support["variance"])),
    )

    util = (support["projected"] / support["annual"] * 100) if support["annual"] else 0
    st.progress(min(max(util / 100, 0), 1.0), text=f"Department projected utilization: {util:.1f}%")

    st.markdown("## KORBI Executive Interpretation")
    st.info(
        "The simulation is positioned on October 1, 2027, after Q1 is complete. July through September are actuals. "
        "October forward combines outstanding commitments and the remaining forecast. A delayed vendor invoice moves "
        "into the month it is now expected to post, so timing changes affect monthly variance without disappearing from the annual outlook."
    )


# ============================================================
# MONTHLY FINANCIALS
# ============================================================

elif page == "Monthly Financials":

    section_title(
        "Monthly Financials",
        "Q1 actuals are complete through September 2027. October is the current month; November through June remain forecast. Every month reconciles to the same annual model used across KORBI."
    )

    sport_options = ["Entire Athletics"]
    if not triage_df.empty and "program_name" in triage_df.columns:
        sport_options += sorted(
            triage_df["program_name"].dropna().astype(str).unique().tolist()
        )

    scope = st.selectbox("View", sport_options)
    monthly_outlook = monthly_financial_outlook(scope)
    scope_totals = _scope_financial_totals(scope)

    if monthly_outlook.empty:
        st.info("No monthly financial model is currently available.")
    else:
        st.markdown("### FY 2027-28 Monthly Plan, Execution & Forecast")

        display_monthly = monthly_outlook.copy()
        currency_columns = [
            "Monthly Plan",
            "Actual Posted",
            "Committed",
            "Remaining Forecast",
            "Projected Month-End",
            "Variance to Plan",
        ]
        for col in currency_columns:
            display_monthly[col] = display_monthly[col].apply(money_zero)

        st.dataframe(
            display_monthly,
            width="stretch",
            hide_index=True,
        )

        q1_actual = monthly_outlook.loc[
            monthly_outlook["Status"] == "EXECUTED", "Actual Posted"
        ].sum()
        commitments = monthly_outlook["Committed"].sum()
        remaining_forecast = monthly_outlook["Remaining Forecast"].sum()
        projected = monthly_outlook["Projected Month-End"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Q1 Actual Posted", money_zero(q1_actual))
        m2.metric("Committed Obligations", money_zero(commitments))
        m3.metric("Remaining Forecast", money_zero(remaining_forecast))
        m4.metric("Projected FY Outlook", money_zero(projected))

        annual_plan = safe_float(scope_totals.get("annual"))
        variance = annual_plan - projected
        v1, v2, v3 = st.columns(3)
        v1.metric("Annual Plan", money_zero(annual_plan))
        v2.metric("Projected FY Outlook", money_zero(projected))
        v3.metric(
            "Projected Favorable Variance" if variance >= 0 else "Projected Unfavorable Variance",
            money_zero(abs(variance)),
        )

        st.markdown(
            '<div class="neutral-note"><strong>How to read the monthly model:</strong> '
            'Monthly Plan is the original planned spend. Actual Posted is what hit the ledger. '
            'Committed is approved money still expected to post. Remaining Forecast is expected spend not yet committed. '
            'Projected Month-End adds those three operating buckets. Variance to Plan is Monthly Plan minus Projected Month-End. '
            'If a September invoice did not post on time, the commitment carries into October rather than disappearing.</div>',
            unsafe_allow_html=True,
        )

        # Surface timing pressure when a favorable month is followed by an unfavorable one.
        timing_notes = []
        for i in range(len(monthly_outlook) - 1):
            this_row = monthly_outlook.iloc[i]
            next_row = monthly_outlook.iloc[i + 1]
            if this_row["Variance to Plan"] > 1000 and next_row["Variance to Plan"] < -1000:
                timing_notes.append(
                    f"{this_row['Month']} is {money_zero(this_row['Variance to Plan'])} favorable while "
                    f"{next_row['Month']} is {money_zero(abs(next_row['Variance to Plan']))} unfavorable; "
                    "that pattern may reflect timing or a commitment rolling into the following month."
                )

        if timing_notes:
            st.markdown("### KORBI Timing Watch")
            for note in timing_notes[:3]:
                st.markdown(
                    f'<div style="color:#263746;font-weight:600;line-height:1.5;margin:.35rem 0;">'
                    f'• {html.escape(note)}</div>',
                    unsafe_allow_html=True,
                )

        dataframe_download(
            monthly_outlook,
            "korbi_monthly_financials.csv",
            "Download Monthly Financials CSV",
        )

    if not financial_history_df.empty:
        with st.expander("Prior-Year / Historical Financial Data"):
            st.dataframe(financial_history_df, width="stretch", hide_index=True)


# ============================================================
# SPORT BUDGETS
# ============================================================

elif page == "Sport Budgets":

    section_title(
        "Sport Budgets",
        "Each program uses its own connected operating budget. Category detail, Q1 actuals, commitments, remaining forecast, projected year-end position, request activity, and Executive Dashboard health all reconcile to the same program totals."
    )

    if triage_df.empty or "program_name" not in triage_df.columns:
        st.warning("Sport-level triage/budget data is not loaded.")
    else:
        programs = sorted(triage_df["program_name"].dropna().astype(str).unique())
        selection = st.selectbox("Program", programs)
        metrics = program_metrics(selection)

        if metrics:
            status, css = program_health(metrics["utilization"])

            st.markdown(f"## {selection} Financial Position")
            st.caption(
                "This is the same financial position used to determine the program's health on the Executive Dashboard."
            )

            b1, b2, b3, b4, b5, b6 = st.columns(6)
            b1.metric("Annual Budget", compact_money(metrics["annual"]))
            b2.metric("Q1 Actual", compact_money(metrics["actual"]))
            b3.metric("Committed", compact_money(metrics["committed"]))
            b4.metric("Remaining Forecast", compact_money(metrics["remaining_forecast"]))
            b5.metric("Projected Year-End", compact_money(metrics["projected"]))
            b6.metric("Projected Remaining", compact_money(metrics["remaining"]))

            st.progress(
                min(max(metrics["utilization"] / 100, 0), 1.0),
                text=f"Projected utilization: {metrics['utilization']:.1f}% — {status}"
            )

            if status == "OVER BUDGET":
                st.error("OVER BUDGET — projected expenses exceed the approved annual program budget.")
            elif status == "HIGH RISK":
                st.error("HIGH RISK — very little year-end flexibility remains.")
            elif status == "CAUTION":
                st.warning("CAUTION — financial flexibility is becoming limited.")
            elif status == "MONITOR":
                st.info("MONITOR — the program remains within plan but should watch remaining flexibility.")
            else:
                st.info("HEALTHY — the current projection remains comfortably within the annual plan.")

            st.caption(
                "Q1 Actual + Committed + Remaining Forecast = Projected Year-End. "
                "Approved purchase requests immediately move into Committed until they later post as actual spend."
            )

            st.markdown(f"## {selection} Operating Budget Detail")
            st.caption(
                "Simulated category allocations for the program operating budget. These categories reconcile exactly to the program totals above. "
                "Shared athletics administration and department-wide costs remain in the department shared-cost budget rather than being duplicated inside team budgets."
            )

            breakdown = program_budget_breakdown(selection)
            if breakdown.empty:
                st.info("No program budget detail is available.")
            else:
                detail_view = breakdown.copy()
                st.dataframe(
                    accounting_table(
                        detail_view,
                        currency_cols=[
                            "Annual Budget",
                            "Q1 Actual",
                            "Committed",
                            "Remaining Forecast",
                            "Projected Year-End",
                            "Projected Remaining",
                        ],
                        percent_cols=["Utilization"],
                    ),
                    width="stretch",
                    hide_index=True,
                )

                st.markdown("### Program Budget Reconciliation")
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("Category Budget Total", money(breakdown["Annual Budget"].sum()))
                t2.metric("Category Q1 Actual Total", money(breakdown["Q1 Actual"].sum()))
                t3.metric("Category Projected Total", money(breakdown["Projected Year-End"].sum()))
                t4.metric(
                    "Difference to Program Budget",
                    money_zero(metrics["annual"] - breakdown["Annual Budget"].sum()),
                )
                st.caption(
                    f"{selection}'s category budget totals equal its {money(metrics['annual'])} annual program budget. "
                    "The projected total above is the same value used on the Executive Dashboard."
                )

        request_view = request_status_table(selection)
        department_requests = request_status_table()

        st.markdown(f"## Request Center — {selection}")
        st.caption(
            f"This view contains {selection} requests only. Department-wide requests are managed on the Purchase Requests page."
        )

        if request_view.empty:
            st.info(f"No requests are currently loaded for {selection}.")
        else:
            open_count = int((request_view["request_status"] == "OPEN").sum())
            allocated_count = int((request_view["request_type"] == "ALLOCATED").sum())
            approved_count = int((request_view["request_status"] == "APPROVED").sum())
            denied_count = int((request_view["request_status"] == "DENIED").sum())
            department_open_count = int((department_requests["request_status"] == "OPEN").sum()) if not department_requests.empty else 0

            r1, r2, r3, r4 = st.columns(4)
            r1.metric(f"Open — {selection}", open_count)
            r2.metric("Allocated / Planned", allocated_count)
            r3.metric("Approved", approved_count)
            r4.metric("Denied", denied_count)

            st.caption(
                f"{selection}: {open_count} open request{'' if open_count == 1 else 's'} | "
                f"Entire Athletics: {department_open_count} open request{'' if department_open_count == 1 else 's'}."
            )

            request_columns = [
                c for c in [
                    "request_id", "description", "category_code", "priority", "amount",
                    "request_type", "request_status", "requestor_name", "reviewed_by", "review_date"
                ] if c in request_view.columns
            ]

            open_tab, allocated_tab, approved_tab, denied_tab = st.tabs(
                ["Open Requests", "Allocated Requests", "Approved Requests", "Denied Requests"]
            )

            def show_request_rows(df, empty_text):
                if df.empty:
                    st.info(empty_text)
                    return
                st.dataframe(
                    accounting_table(df[request_columns].copy(), currency_cols=["amount"]),
                    width="stretch",
                    hide_index=True,
                )

            with open_tab:
                show_request_rows(
                    request_view[request_view["request_status"] == "OPEN"],
                    f"No open requests for {selection}."
                )

            with allocated_tab:
                show_request_rows(
                    request_view[request_view["request_type"] == "ALLOCATED"],
                    f"No requests are explicitly identified as allocated/planned for {selection}."
                )
                st.caption(
                    "Allocated / Planned is a request type, not an approval. A planned item still follows the same review and purchasing controls."
                )

            with approved_tab:
                approved_rows = request_view[request_view["request_status"] == "APPROVED"]
                show_request_rows(approved_rows, f"No approved requests for {selection}.")
                if not approved_rows.empty:
                    approved_value = pd.to_numeric(approved_rows["amount"], errors="coerce").fillna(0).sum()
                    st.metric("Approved Request Value", money(approved_value))
                    st.caption(
                        "Approved requests are treated as committed money even before the vendor invoice posts. "
                        "When the invoice becomes an actual, KORBI moves the amount out of committed rather than adding it again."
                    )

            with denied_tab:
                show_request_rows(
                    request_view[request_view["request_status"] == "DENIED"],
                    f"No denied requests for {selection}."
                )

        st.markdown("## Program Financial Interpretation")
        if metrics:
            status, _ = program_health(metrics["utilization"])
            st.markdown(
                f'<div class="neutral-note"><strong>{html.escape(selection)}</strong> is currently classified as '
                f'<strong>{status}</strong> at <strong>{metrics["utilization"]:.1f}%</strong> projected utilization. '
                f'Projected year-end spend is <strong>{money(metrics["projected"])}</strong> against an annual program budget of '
                f'<strong>{money(metrics["annual"])}</strong>, leaving <strong>{money(metrics["remaining"])}</strong> of projected flexibility. '
                'This is the exact same program position used by the Executive Dashboard and Purchase Request analysis.</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# PURCHASE REQUESTS
# ============================================================

elif page == "Purchase Requests":

    section_title(
        "Purchase Requests",
        "KORBI financial analysis, coach impact, and human approval workflow."
    )

    if triage_df.empty:
        st.error("No request triage data is loaded.")
        st.stop()

    # Always derive current status from the saved decision layer.
    request_master = request_status_table()

    # Use the same primary-button treatment as the Home page instead of Streamlit's
    # dark segmented control so navigation styling stays consistent across KORBI.
    if "purchase_request_mode" not in st.session_state:
        st.session_state["purchase_request_mode"] = "Awaiting Review"

    pr1, pr2, pr3 = st.columns(3)

    if pr1.button(
        "Awaiting Review",
        key="purchase_mode_awaiting",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["purchase_request_mode"] = "Awaiting Review"

    if pr2.button(
        "All Requests",
        key="purchase_mode_all",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["purchase_request_mode"] = "All Requests"

    if pr3.button(
        "Reviewed",
        key="purchase_mode_reviewed",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["purchase_request_mode"] = "Reviewed"

    mode = st.session_state["purchase_request_mode"]
    st.caption(f"Showing: {mode}")

    if mode == "Awaiting Review":
        view_df = request_master[
            request_master["request_status"] == "OPEN"
        ].copy()

        if not view_df.empty:
            if "percent_with_request" in view_df.columns:
                view_df["_sort_risk"] = pd.to_numeric(
                    view_df["percent_with_request"],
                    errors="coerce"
                ).fillna(0)
            else:
                view_df["_sort_risk"] = 0

            if "amount" in view_df.columns:
                view_df["_sort_amount"] = pd.to_numeric(
                    view_df["amount"],
                    errors="coerce"
                ).fillna(0)
            else:
                view_df["_sort_amount"] = 0

            view_df = (
                view_df
                .sort_values(
                    by=["_sort_risk", "_sort_amount"],
                    ascending=[False, False]
                )
                .head(10)
                .drop(
                    columns=["_sort_risk", "_sort_amount"],
                    errors="ignore"
                )
            )

    elif mode == "Reviewed":
        view_df = request_master[request_master["manager_decision"].notna()].copy() if "manager_decision" in request_master.columns else request_master.iloc[0:0].copy()
    else:
        view_df = request_master.copy()

    if view_df.empty:
        st.success("No requests in this view.")
        st.stop()

    labels = [
        f"{r.get('request_id', '')} — {r.get('program_name', '')} — "
        f"{r.get('description', '')} — {money(r.get('amount'))}"
        for _, r in view_df.iterrows()
    ]

    selected = st.selectbox("Select request", labels)
    raw_row = view_df.iloc[labels.index(selected)].to_dict()
    row = live_request_row(raw_row)

    recommendation, suggestion = actionable_recommendation(row)

    st.markdown(f"### {row.get('program_name', '')} — {row.get('description', '')}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Request", money(row.get("amount")))
    c2.metric("Priority", str(row.get("priority", "")))
    c3.metric("Before", pct(row.get("baseline_percent")))
    c4.metric("After", pct(row.get("percent_with_request")))

    st.markdown("#### KORBI Recommendation")
    st.info(recommendation)
    st.markdown(
        f'<div class="premium-note">{html.escape(str(suggestion))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Coach Impact")
    st.markdown(
        f'<div class="premium-note">{html.escape(coach_impact(row))}</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Budget Before Request")
        for label, key in [
            ("Annual operating budget", "annual_budget"),
            ("Actuals", "q1_actuals"),
            ("Open / committed", "open_pos"),
            ("Scheduled future", "scheduled_future"),
            ("Expected future", "expected_future"),
            ("Projected remaining", "baseline_remaining"),
        ]:
            st.write(f"**{label}:** {money(row.get(key))}")

    with right:
        st.markdown("#### Budget After Request")
        st.write(f"**Request amount:** {money(row.get('amount'))}")
        st.write(f"**Projected year-end:** {money(row.get('projected_with_request'))}")
        st.write(f"**Projected remaining:** {money(row.get('remaining_with_request'))}")
        st.write(f"**Projected utilization:** {pct(row.get('percent_with_request'))}")

    st.markdown("#### Budget Impact")
    st.markdown(
        f'<div class="neutral-note">{html.escape(budget_impact(row))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Risk")
    risk_text = risk_summary(row)
    if safe_float(row.get("percent_with_request")) > 100:
        st.error(risk_text)
    elif safe_float(row.get("percent_with_request")) >= 95:
        st.warning(risk_text)
    else:
        st.write(risk_text)

    st.markdown("---")
    st.markdown("## Management Decision")

    existing_requestor = requestor_name(raw_row)
    if not existing_requestor and "requestor_name" in raw_row:
        existing_requestor = str(raw_row.get("requestor_name", ""))

    requestor = st.text_input(
        "Requestor / Coach Name",
        value=existing_requestor,
        placeholder="Enter the requestor name so KORBI can prepare the response.",
        key=f"requestor_{row.get('request_id', '')}",
    )

    existing_decision = str(raw_row.get("manager_decision", "")).upper().strip()
    decision_options = ["APPROVE", "DEFER", "DENY"]
    default_index = decision_options.index(existing_decision) if existing_decision in decision_options else 0

    decision = st.radio(
        "Decision",
        decision_options,
        index=default_index,
        horizontal=True,
        key=f"decision_{row.get('request_id', '')}",
    )

    next_action = ""
    target_fiscal_year = ""
    anticipated_next_year_budget = 0.0

    if decision == "DEFER":
        st.markdown("### Deferred Request Next Step")

        next_action_options = [
            "Reconsider later this fiscal year",
            "Elevate to Director of Athletics for additional funding",
            "Seek alternative / external funding",
            "Carry forward to FY 2028-29 budget",
            "Elevate to AD; if unfunded, carry forward to FY 2028-29",
        ]

        saved_next_action = str(raw_row.get("next_action", "")).strip()
        next_default = (
            next_action_options.index(saved_next_action)
            if saved_next_action in next_action_options
            else 4
        )

        next_action = st.selectbox(
            "Next Action",
            next_action_options,
            index=next_default,
            key=f"next_action_{row.get('request_id', '')}",
        )

        if "FY 2028-29" in next_action:
            target_fiscal_year = "FY 2028-29"
            saved_next_budget = safe_float(raw_row.get("anticipated_next_year_budget"))
            default_next_budget = saved_next_budget if saved_next_budget > 0 else round(safe_float(row.get("amount")) * 1.05, -1)

            anticipated_next_year_budget = st.number_input(
                "Anticipated FY 2028-29 Budget ($)",
                min_value=0.0,
                value=float(default_next_budget),
                step=100.0,
                format="%.0f",
                key=f"next_budget_{row.get('request_id', '')}",
            )

            st.caption(
                "KORBI will retain this deferred need for the next budget cycle so it is not lost when FY 2028-29 planning begins."
            )
        else:
            target_fiscal_year = "FY 2027-28"

    notes = st.text_area(
        "Manager notes",
        value=str(raw_row.get("manager_notes", "")) if str(raw_row.get("manager_notes", "")).lower() != "nan" else "",
        placeholder="Optional context, conditions, offsets, or follow-up instructions.",
        key=f"notes_{row.get('request_id', '')}",
    )

    # Preview the exact rationale that will be stored with the decision.
    rationale_preview = decision_rationale(
        row,
        decision,
        next_action=next_action,
        target_fiscal_year=target_fiscal_year,
        anticipated_next_year_budget=anticipated_next_year_budget,
    )
    email_preview = requestor_email(
        row,
        decision,
        requestor,
        notes,
        next_action=next_action,
        target_fiscal_year=target_fiscal_year,
        anticipated_next_year_budget=anticipated_next_year_budget,
    )

    st.markdown("### KORBI Decision Explanation")
    st.info(rationale_preview.replace("$", r"\$"))

    st.markdown("### Email-Ready Response to Requestor")
    st.caption(
        "The response wraps vertically so the full message can be read without horizontal scrolling. "
        "KORBI saves this wording with the decision so the historical explanation does not change later."
    )
    wrapped_email_box(email_preview)

    if st.button("Save Management Decision", type="primary"):
        record = save_decision(
            row=row,
            recommendation=recommendation,
            suggestion=suggestion,
            decision=decision,
            reviewer=reviewer,
            notes=notes,
            requestor=requestor,
            next_action=next_action,
            target_fiscal_year=target_fiscal_year,
            anticipated_next_year_budget=anticipated_next_year_budget,
        )
        st.success(
            f"{row.get('request_id', '')} saved as {decision}. KORBI has updated the decision layer, request status, "
            "sport budget impact, and department forecast."
        )
        st.rerun()


# ============================================================
# REVENUE & FUNDING
# ============================================================

elif page == "Revenue & Funding":

    section_title(
        "Revenue & Funding",
        "University support, student fees, external revenue, and one-time rebuild funding."
    )

    support = university_support_projection()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Modeled University Support", money(support["modeled_university_support"]))
    c2.metric("Student-Fee Support", money(support["student_fees"]))
    c3.metric("External / Earned Revenue", money(support["external_revenue"]))
    c4.metric("One-Time Rebuild Funding", money(support["one_time_rebuild"]))

    st.markdown("## University Support Impact")

    st.markdown(
        f"""
        <div class="support-card">
            <div class="support-kicker">Projected University Support Required</div>
            <div class="support-value">{money(support["required_support"])}</div>
            <div class="support-copy">
                Current external / earned athletics revenue reduces modeled university support
                by <strong>{money(support["external_reduction"])}</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "KORBI keeps university support separate from externally generated athletics revenue. "
        "One-time rebuild funding is also kept separate from recurring operating revenue."
    )

    if funding_df.empty:
        st.info("No detailed revenue/funding dataset is loaded.")
    else:
        st.dataframe(funding_df, width="stretch", hide_index=True)
        dataframe_download(
            funding_df,
            "korbi_revenue_funding.csv",
            "Download Revenue & Funding CSV",
        )


# ============================================================
# APPROVED / PURCHASE ORDERS
# ============================================================

elif page == "Approved / Purchase Orders":

    section_title(
        "Approved / Purchase Orders",
        "Approved obligations and open purchase orders with expected invoice dates. These records reconcile to KORBI's committed balance and explain what the department has already obligated but has not yet posted as actual expense."
    )

    po_df = approved_purchase_orders_df()

    if po_df.empty:
        st.info("No approved purchase orders are currently modeled.")
    else:
        total_po = pd.to_numeric(po_df["Approved Amount"], errors="coerce").fillna(0).sum()
        remaining_po = pd.to_numeric(po_df["Remaining PO Balance"], errors="coerce").fillna(0).sum()
        dept_committed = safe_float(department_financial_summary().get("committed"))
        reconciliation = dept_committed - remaining_po

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Open Purchase Orders", f"{len(po_df):,}")
        p2.metric("Approved PO Value", money_zero(total_po))
        p3.metric("Remaining PO Balance", money_zero(remaining_po))
        p4.metric("Reconciliation Difference", money_zero(reconciliation))

        st.markdown(
            '<div class="premium-note"><strong>Financial rule:</strong> Approved purchase orders are already committed money. '
            'When an invoice posts, the amount moves from <strong>Committed</strong> to <strong>Actual Posted</strong>; '
            'Projected Year-End does not increase again because KORBI is moving the same obligation between buckets.</div>',
            unsafe_allow_html=True,
        )

        f1, f2, f3 = st.columns(3)
        with f1:
            programs = ["All Athletics"] + sorted(po_df["Program"].dropna().astype(str).unique().tolist())
            po_program = st.selectbox("Program / Department", programs, key="po_program_filter")
        with f2:
            categories = ["All Categories"] + sorted(po_df["Category"].dropna().astype(str).unique().tolist())
            po_category = st.selectbox("Category", categories, key="po_category_filter")
        with f3:
            months = ["All Posting Months"] + list(dict.fromkeys(po_df["Expected Posting Month"].astype(str).tolist()))
            po_month = st.selectbox("Expected Posting Month", months, key="po_month_filter")

        view = po_df.copy()
        if po_program != "All Athletics":
            view = view[view["Program"].astype(str) == po_program]
        if po_category != "All Categories":
            view = view[view["Category"].astype(str) == po_category]
        if po_month != "All Posting Months":
            view = view[view["Expected Posting Month"].astype(str) == po_month]

        st.markdown("## Open PO Detail")
        detail = view.copy()
        for c in ["Approved Amount", "Amount Invoiced", "Remaining PO Balance"]:
            detail[c] = detail[c].apply(money_zero)
        st.markdown(
            '<div class="korbi-table-wrap">' +
            detail[["PO #", "Request #", "Program", "Vendor", "Description", "Category", "Approved Amount", "Approval Date", "Expected Invoice / Delivery", "Expected Posting Month", "PO Status", "Remaining PO Balance"]]
            .to_html(index=False, classes="korbi-table", border=0, escape=True) +
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("## Program Commitment Summary")
        summary = (
            po_df.groupby("Program", dropna=False)
            .agg(Open_POs=("PO #", "count"), Approved_Value=("Approved Amount", "sum"), Remaining_PO_Balance=("Remaining PO Balance", "sum"))
            .reset_index()
            .rename(columns={"Open_POs":"Open POs", "Approved_Value":"Approved Value", "Remaining_PO_Balance":"Remaining PO Balance"})
        )
        summary["Approved Value"] = summary["Approved Value"].apply(money_zero)
        summary["Remaining PO Balance"] = summary["Remaining PO Balance"].apply(money_zero)
        st.markdown(
            '<div class="korbi-table-wrap">' + summary.to_html(index=False, classes="korbi-table", border=0, escape=True) + '</div>',
            unsafe_allow_html=True,
        )

        dataframe_download(po_df, "korbi_approved_purchase_orders.csv", "Download Approved / Purchase Orders CSV")


# ============================================================
# DENIED REQUESTS
# ============================================================

elif page == "Denied Requests":

    section_title(
        "Denied Requests",
        "Requests that were declined and removed from the current committed forecast. Denied items remain visible for auditability but do not consume budget unless they are resubmitted or intentionally moved to Deferred & Future Needs."
    )

    denied_df = denied_requests_df()
    if denied_df.empty:
        st.info("No denied requests are currently tracked.")
    else:
        total_denied = pd.to_numeric(denied_df["Amount"], errors="coerce").fillna(0).sum()
        programs_affected = denied_df["Program"].dropna().astype(str).nunique()
        live_denied = int((denied_df["Source"].astype(str) == "Live KORBI Decision").sum())

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Denied Requests", f"{len(denied_df):,}")
        d2.metric("Denied Request Value", money_zero(total_denied))
        d3.metric("Programs Affected", f"{programs_affected:,}")
        d4.metric("Live Management Denials", f"{live_denied:,}")

        f1, f2 = st.columns(2)
        with f1:
            options = ["All Athletics"] + sorted(denied_df["Program"].dropna().astype(str).unique().tolist())
            denied_program = st.selectbox("Program / Department", options, key="denied_program_filter")
        with f2:
            denied_source = st.selectbox("Source", ["All Sources"] + sorted(denied_df["Source"].astype(str).unique().tolist()), key="denied_source_filter")

        view = denied_df.copy()
        if denied_program != "All Athletics":
            view = view[view["Program"].astype(str) == denied_program]
        if denied_source != "All Sources":
            view = view[view["Source"].astype(str) == denied_source]

        display = view.copy()
        display["Amount"] = display["Amount"].apply(money_zero)
        st.markdown(
            '<div class="korbi-table-wrap">' +
            display[["Request #", "Program", "Description", "Amount", "Denial Date", "Reason Denied", "Reviewer", "Resubmittable", "Future Budget Consideration"]]
            .to_html(index=False, classes="korbi-table", border=0, escape=True) +
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="premium-note"><strong>Planning note:</strong> If a denied need should remain visible for a future fiscal year, '
            'change the management action to <strong>DEFER</strong> rather than DENY so KORBI carries it into Deferred & Future Needs.</div>',
            unsafe_allow_html=True,
        )
        dataframe_download(denied_df, "korbi_denied_requests.csv", "Download Denied Requests CSV")


# ============================================================
# CSU BENCHMARKING
# ============================================================

elif page == "CSU Benchmarking":

    section_title(
        "CSU Benchmarking",
        "Historical CSU Division II benchmarks to help Sonoma State build realistic operating budgets for its returning sports."
    )

    st.info(
        "Benchmark data is historical EADA-based comparison data. KORBI uses it as a planning reference — not as a "
        "required spending target for the Fall 2027 restart."
    )

    def peer_summary_frame():
        if peer_comparison_df.empty:
            return pd.DataFrame()

        df = peer_comparison_df.copy()
        school_col = first_existing_column(df, ["school_name", "school", "institution", "Institution"])
        id_col = first_existing_column(df, ["school_id", "institution_id", "id"])
        athlete_col = first_existing_column(df, ["total_athletes", "athletes", "participants"])
        expense_col = first_existing_column(df, ["total_expenses", "total_expense", "expenses", "athletics_expenses"])
        team_exp_col = first_existing_column(df, ["team_expenses", "team_expense", "allocated_team_expenses"])
        unalloc_col = first_existing_column(df, ["unallocated_amount", "unallocated", "not_allocated", "unallocated_expenses"])
        share_col = first_existing_column(df, ["unallocated_share", "unallocated_share_pct", "unallocated_percent", "unallocated_pct"])
        epa_col = first_existing_column(df, ["expense_per_athlete", "expenses_per_athlete", "cost_per_athlete"])

        out = pd.DataFrame()
        out["School"] = df[school_col].astype(str) if school_col else [f"Peer {i+1}" for i in range(len(df))]
        if id_col:
            out["School ID"] = df[id_col].astype(str)
        out["Athletes"] = pd.to_numeric(df[athlete_col], errors="coerce") if athlete_col else pd.NA
        out["Total Expense"] = pd.to_numeric(df[expense_col], errors="coerce") if expense_col else pd.NA
        out["Team Expense"] = pd.to_numeric(df[team_exp_col], errors="coerce") if team_exp_col else pd.NA
        out["Unallocated"] = pd.to_numeric(df[unalloc_col], errors="coerce") if unalloc_col else pd.NA
        out["Unallocated %"] = pd.to_numeric(df[share_col], errors="coerce") if share_col else pd.NA
        out["Expense / Athlete"] = pd.to_numeric(df[epa_col], errors="coerce") if epa_col else pd.NA

        if out["Expense / Athlete"].isna().all() and not out["Total Expense"].isna().all():
            denom = pd.to_numeric(out["Athletes"], errors="coerce").replace(0, pd.NA)
            out["Expense / Athlete"] = out["Total Expense"] / denom

        if out["Unallocated %"].isna().all() and not out["Unallocated"].isna().all():
            denom = pd.to_numeric(out["Total Expense"], errors="coerce").replace(0, pd.NA)
            out["Unallocated %"] = out["Unallocated"] / denom * 100

        return out

    def team_source_frame():
        if not team_benchmark_df.empty:
            return team_benchmark_df.copy()
        if not team_summary_df.empty:
            return team_summary_df.copy()
        return pd.DataFrame()

    peers = peer_summary_frame()

    if peers.empty:
        st.warning("Peer comparison dataset is not loaded.")
    else:
        is_sonoma = peers["School"].astype(str).str.contains("Sonoma", case=False, na=False)
        if "School ID" in peers.columns:
            is_sonoma = is_sonoma | peers["School ID"].astype(str).str.upper().eq("SSU")

        sonoma_rows = peers[is_sonoma]
        peer_only = peers[~is_sonoma].copy()

        if sonoma_rows.empty:
            st.warning("KORBI could not identify the Sonoma State row in the peer comparison dataset.")
            sonoma = None
        else:
            sonoma = sonoma_rows.iloc[0]

        if sonoma is not None and not peer_only.empty:
            sonoma_exp = safe_float(sonoma.get("Total Expense"))
            peer_avg_exp = pd.to_numeric(peer_only["Total Expense"], errors="coerce").mean()
            peer_avg_epa = pd.to_numeric(peer_only["Expense / Athlete"], errors="coerce").mean()

            tmp = peer_only.copy()
            tmp["_distance"] = (pd.to_numeric(tmp["Total Expense"], errors="coerce") - sonoma_exp).abs()
            closest = tmp.sort_values("_distance").iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Sonoma Historical Expense", compact_money(sonoma_exp))
            c2.metric("CSU Peer Average", compact_money(peer_avg_exp))
            c3.metric("Sonoma Expense / Athlete", compact_money(sonoma.get("Expense / Athlete")))
            c4.metric("Closest Spending Peer", str(closest.get("School", "")))

            st.markdown(
                f'<div class="benchmark-note">Closest total-spend comparator: '
                f'<strong>{html.escape(str(closest.get("School", "")))}</strong> at '
                f'<strong>{html.escape(money(closest.get("Total Expense")))}</strong>. '
                f'Peer-average expense per athlete: approximately '
                f'<strong>{html.escape(money(peer_avg_epa))}</strong>.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("## Historical Department Comparison")

        pretty = peers.copy()
        for col in ["Total Expense", "Team Expense", "Unallocated", "Expense / Athlete"]:
            if col in pretty.columns:
                pretty[col] = pretty[col].apply(lambda x: compact_money(x) if pd.notna(x) else "-")
        if "Unallocated %" in pretty.columns:
            pretty["Unallocated %"] = pretty["Unallocated %"].apply(lambda x: f"{safe_float(x):.1f}%" if pd.notna(x) else "-")
        if "Athletes" in pretty.columns:
            pretty["Athletes"] = pretty["Athletes"].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "-")

        st.markdown(
            '<div class="korbi-table-wrap">' + pretty.to_html(index=False, classes="korbi-table", border=0, escape=True) + '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("## Choose a Comparator")
        comparator_options = peer_only["School"].astype(str).tolist() if not peer_only.empty else []

        if comparator_options and sonoma is not None:
            default_name = str(closest.get("School")) if 'closest' in locals() else comparator_options[0]
            default_idx = comparator_options.index(default_name) if default_name in comparator_options else 0
            comparator_name = st.selectbox("Compare Sonoma State with", comparator_options, index=default_idx)
            comparator = peer_only[peer_only["School"] == comparator_name].iloc[0]

            a, b, c, d = st.columns(4)
            a.metric("Sonoma Total Expense", compact_money(sonoma.get("Total Expense")))
            b.metric(f"{comparator_name} Expense", compact_money(comparator.get("Total Expense")))
            variance = safe_float(sonoma.get("Total Expense")) - safe_float(comparator.get("Total Expense"))
            c.metric("Expense Difference", compact_money(abs(variance)), delta="Sonoma higher" if variance > 0 else "Sonoma lower")
            d.metric("Comparator Athletes", f"{int(safe_float(comparator.get('Athletes'))):,}")

            # ------------------------------------------------
            # SPORT SPONSORSHIP / HISTORICAL TEAM EXPENSE
            # ------------------------------------------------
            teams = team_source_frame()
            if teams.empty:
                st.info("Sport-level peer benchmark data is not loaded.")
            else:
                school_col = first_existing_column(teams, ["school_name", "school", "institution", "Institution"])
                school_id_col = first_existing_column(teams, ["school_id", "institution_id"])
                sport_col = first_existing_column(teams, ["sport_name", "sport", "team_name", "sports"])
                gender_col = first_existing_column(teams, ["gender", "sex", "men_women", "team_gender"])
                expense_col = first_existing_column(teams, ["expenses", "expense", "team_expenses", "total_expenses", "operating_expense"])

                if sport_col and (school_col or school_id_col):
                    temp = teams.copy()
                    temp["_school"] = temp[school_col].astype(str) if school_col else temp[school_id_col].astype(str)
                    temp["_sport"] = temp[sport_col].astype(str).str.strip()

                    if gender_col:
                        gender = temp[gender_col].astype(str).str.upper().str.strip()
                        prefix = gender.map(lambda x: "Men's " if x.startswith("M") else ("Women's " if x.startswith("W") else ""))
                        temp["Sport"] = prefix + temp["_sport"]
                    else:
                        temp["Sport"] = temp["_sport"]

                    if expense_col:
                        temp["Historical Expense"] = pd.to_numeric(temp[expense_col], errors="coerce").fillna(0)
                    else:
                        temp["Historical Expense"] = 0.0

                    sonoma_mask = temp["_school"].str.contains("Sonoma", case=False, na=False) | temp["_school"].str.upper().eq("SSU")
                    comp_mask = temp["_school"].astype(str).eq(comparator_name)

                    # Some team datasets may use school IDs while the peer file uses full names.
                    if not comp_mask.any() and "School ID" in peer_only.columns and school_id_col:
                        comp_id = str(comparator.get("School ID", ""))
                        comp_mask = temp["_school"].astype(str).str.upper().eq(comp_id.upper())

                    st.markdown("### Sport Sponsorship Comparison")
                    all_schools = temp["_school"].dropna().astype(str).unique().tolist()
                    sport_names = sorted(temp["Sport"].dropna().astype(str).unique().tolist())
                    matrix_rows = []
                    for school in all_schools:
                        row_data = {"School": school}
                        school_sports = set(temp.loc[temp["_school"] == school, "Sport"].astype(str))
                        for sport in sport_names:
                            row_data[sport] = "YES" if sport in school_sports else "—"
                        matrix_rows.append(row_data)
                    matrix = pd.DataFrame(matrix_rows)
                    if not matrix.empty:
                        st.markdown(
                            '<div class="korbi-table-wrap">' + matrix.to_html(index=False, classes="korbi-table", border=0, escape=True) + '</div>',
                            unsafe_allow_html=True,
                        )

                    st.markdown("### Sonoma State vs Comparator — Historical Sport Expense")
                    sonoma_sport = temp[sonoma_mask].groupby("Sport")["Historical Expense"].sum().rename("Sonoma Historical")
                    comp_sport = temp[comp_mask].groupby("Sport")["Historical Expense"].sum().rename(f"{comparator_name} Historical")
                    peer_avg = temp.groupby(["_school", "Sport"])["Historical Expense"].sum().reset_index().groupby("Sport")["Historical Expense"].mean().rename("Peer Average")

                    sport_compare = pd.concat([sonoma_sport, comp_sport, peer_avg], axis=1).fillna(0).reset_index()
                    if not sport_compare.empty:
                        sport_compare["Difference vs Comparator"] = sport_compare["Sonoma Historical"] - sport_compare[f"{comparator_name} Historical"]
                        comp_denom = sport_compare[f"{comparator_name} Historical"].replace(0, pd.NA)
                        sport_compare["% Difference"] = sport_compare["Difference vs Comparator"] / comp_denom * 100

                        display_compare = sport_compare.copy()
                        for col in ["Sonoma Historical", f"{comparator_name} Historical", "Peer Average", "Difference vs Comparator"]:
                            display_compare[col] = display_compare[col].apply(compact_money)
                        display_compare["% Difference"] = display_compare["% Difference"].apply(
                            lambda x: f"{safe_float(x):.1f}%" if pd.notna(x) else "-"
                        )
                        st.markdown(
                            '<div class="korbi-table-wrap">' + display_compare.to_html(index=False, classes="korbi-table", border=0, escape=True) + '</div>',
                            unsafe_allow_html=True,
                        )

                        chart = sport_compare.set_index("Sport")[["Sonoma Historical", f"{comparator_name} Historical", "Peer Average"]]
                        st.bar_chart(chart, height=360)

                        if sonoma is not None:
                            sonoma_unalloc = safe_float(sonoma.get("Unallocated %"))
                            peer_unalloc = pd.to_numeric(peer_only["Unallocated %"], errors="coerce").mean()
                            st.markdown("### KORBI Benchmark View")
                            st.info(
                                f"Sonoma State's historical unallocated share is {sonoma_unalloc:.1f}% versus a CSU peer average of "
                                f"approximately {peer_unalloc:.1f}%. KORBI should use peer sport-level expenses as a range and planning "
                                "reference when rebuilding Fall 2027 budgets — not simply copy another school's spending level."
                            )
                else:
                    st.info("The team benchmark dataset is loaded, but KORBI could not identify school and sport fields.")

        dataframe_download(peers, "korbi_csu_peer_benchmark.csv", "Download Peer Benchmark CSV")


# ============================================================
# FORECAST & VARIANCE
# ============================================================

elif page == "Forecast & Variance":

    section_title(
        "Forecast & Variance",
        "Projected year-end position compared with the annual operating plan."
    )

    if department_df.empty:
        st.warning("Department forecast dataset is not loaded.")
    else:
        view = department_df.copy()

        if "annual_budget" in view.columns and "projected_year_end" in view.columns:
            view["forecast_variance"] = (
                pd.to_numeric(view["annual_budget"], errors="coerce").fillna(0)
                - pd.to_numeric(view["projected_year_end"], errors="coerce").fillna(0)
            )

            view["forecast_utilization_pct"] = (
                pd.to_numeric(view["projected_year_end"], errors="coerce").fillna(0)
                / pd.to_numeric(view["annual_budget"], errors="coerce").replace(0, pd.NA)
                * 100
            )

        currency_cols = [
            c for c in [
                "annual_budget",
                "q1_actual",
                "open_commitments",
                "future_reserved",
                "projected_year_end",
                "uncommitted_reserve",
                "forecast_variance",
            ]
            if c in view.columns
        ]

        percent_cols = [
            "forecast_utilization_pct"
        ] if "forecast_utilization_pct" in view.columns else []

        st.dataframe(
            accounting_table(
                view,
                currency_cols=currency_cols,
                percent_cols=percent_cols,
            ),
            width="stretch",
            hide_index=True,
        )

        st.info(
            "Positive variance should be treated as remaining capacity, not automatically as spendable surplus. "
            "KORBI should continue reserving for known future obligations and uncertainty."
        )


# ============================================================
# OPEN POS & COMMITMENTS
# ============================================================

elif page == "Open POs & Commitments":

    section_title(
        "Open POs & Commitments",
        "Committed spending not yet fully recognized as posted actual expense."
    )

    if ledger_df.empty:
        st.warning("Operational ledger is not loaded.")
    else:
        type_col = first_existing_column(ledger_df, ["transaction_type", "type", "status"])

        if type_col:
            view = ledger_df[
                ledger_df[type_col].astype(str).str.contains(
                    "PO|OPEN|COMMIT", case=False, na=False, regex=True
                )
            ].copy()

            if view.empty:
                st.info("No rows matched open PO / commitment indicators.")
            else:
                st.dataframe(view, width="stretch", hide_index=True)
        else:
            st.dataframe(ledger_df, width="stretch", hide_index=True)


# ============================================================
# PAYROLL & STAFFING
# ============================================================

elif page == "Payroll & Staffing":

    section_title(
        "Payroll & Staffing",
        "Modeled staffing structure and compensation data."
    )

    if staffing_df.empty:
        st.warning("Staffing dataset is not loaded.")
    else:
        st.dataframe(staffing_df, width="stretch", hide_index=True)

        salary_col = first_existing_column(
            staffing_df,
            ["salary", "base_salary", "amount", "cost"]
        )

        if salary_col:
            total = pd.to_numeric(
                staffing_df[salary_col], errors="coerce"
            ).fillna(0).sum()

            st.metric("Modeled Base Compensation", money(total))

            st.info(
                "Staffing is a largely fixed cost. Vacancies, benefits, additional hires, or changes to the "
                "staffing model can materially change year-end operating flexibility."
            )


# ============================================================
# DEFERRED & FUTURE NEEDS
# ============================================================

elif page == "Deferred & Future Needs":

    section_title(
        "Deferred & Future Needs",
        "Track current-year requests that were deferred, elevated, or carried into the next budget cycle so program needs are not lost between fiscal years."
    )

    deferred_df = deferred_future_needs_df()

    if deferred_df.empty:
        st.info("No deferred or future needs are currently tracked.")
    else:
        # Filters
        f1, f2, f3 = st.columns(3)

        with f1:
            program_options = ["All Athletics"] + sorted(
                deferred_df["Program"].dropna().astype(str).unique().tolist()
            )
            deferred_program = st.selectbox(
                "Program / Department",
                program_options,
                key="deferred_program_filter",
            )

        with f2:
            fy_options = ["All Fiscal Years"] + sorted(
                deferred_df["Target Fiscal Year"].dropna().astype(str).unique().tolist()
            )
            deferred_fy = st.selectbox(
                "Target Fiscal Year",
                fy_options,
                key="deferred_fy_filter",
            )

        with f3:
            status_options = ["All Statuses"] + sorted(
                deferred_df["Status"].dropna().astype(str).unique().tolist()
            )
            deferred_status = st.selectbox(
                "Status",
                status_options,
                key="deferred_status_filter",
            )

        filtered_deferred = deferred_df.copy()

        if deferred_program != "All Athletics":
            filtered_deferred = filtered_deferred[
                filtered_deferred["Program"].astype(str) == deferred_program
            ]

        if deferred_fy != "All Fiscal Years":
            filtered_deferred = filtered_deferred[
                filtered_deferred["Target Fiscal Year"].astype(str) == deferred_fy
            ]

        if deferred_status != "All Statuses":
            filtered_deferred = filtered_deferred[
                filtered_deferred["Status"].astype(str) == deferred_status
            ]

        total_deferred = pd.to_numeric(
            filtered_deferred["Deferred Amount"],
            errors="coerce",
        ).fillna(0).sum()

        next_year_total = pd.to_numeric(
            filtered_deferred.loc[
                filtered_deferred["Target Fiscal Year"].astype(str) == "FY 2028-29",
                "Anticipated FY Budget",
            ],
            errors="coerce",
        ).fillna(0).sum()

        carried_count = int(
            (
                filtered_deferred["Target Fiscal Year"].astype(str)
                == "FY 2028-29"
            ).sum()
        )

        programs_affected = filtered_deferred["Program"].dropna().astype(str).nunique()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Deferred Requests", f"{len(filtered_deferred):,}")
        m2.metric("Deferred Value", money_zero(total_deferred))
        m3.metric("FY 2028-29 Planned Need", money_zero(next_year_total))
        m4.metric("Programs Affected", f"{programs_affected:,}")

        st.markdown(
            '<div class="premium-note"><strong>Budget-cycle purpose:</strong> '
            'Every carried-forward request remains visible with its original amount, reason for deferral, '
            'next action, and anticipated future-year budget. This gives Athletics a starting list of unfunded '
            'needs before the next budget cycle begins.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("## Deferred Needs by Program")

        grouped = (
            filtered_deferred.groupby("Program", dropna=False)
            .agg(
                Deferred_Requests=("Request ID", "count"),
                Deferred_Value=("Deferred Amount", "sum"),
                Anticipated_FY_Budget=("Anticipated FY Budget", "sum"),
            )
            .reset_index()
            .rename(
                columns={
                    "Deferred_Requests": "Deferred Requests",
                    "Deferred_Value": "Deferred Value",
                    "Anticipated_FY_Budget": "Anticipated FY Budget",
                }
            )
        )

        grouped["Deferred Value"] = grouped["Deferred Value"].apply(money_zero)
        grouped["Anticipated FY Budget"] = grouped["Anticipated FY Budget"].apply(money_zero)

        st.markdown(
            '<div class="korbi-table-wrap">'
            + grouped.to_html(index=False, classes="korbi-table", border=0, escape=True)
            + '</div>',
            unsafe_allow_html=True,
        )

        st.markdown("## Deferred Request Detail")

        detail_columns = [
            "Program",
            "Purchase Request",
            "Deferred Amount",
            "Reason Deferred",
            "Next Step",
            "Target Fiscal Year",
            "Anticipated FY Budget",
            "Status",
        ]

        detail = filtered_deferred[detail_columns].copy()
        detail["Deferred Amount"] = detail["Deferred Amount"].apply(money_zero)
        detail["Anticipated FY Budget"] = detail["Anticipated FY Budget"].apply(money_zero)

        st.markdown(
            '<div class="korbi-table-wrap">'
            + detail.to_html(index=False, classes="korbi-table", border=0, escape=True)
            + '</div>',
            unsafe_allow_html=True,
        )

        if carried_count > 0:
            st.markdown("## FY 2028-29 Carry-Forward Planning")

            next_year = filtered_deferred[
                filtered_deferred["Target Fiscal Year"].astype(str) == "FY 2028-29"
            ].copy()

            if not next_year.empty:
                planning_total = pd.to_numeric(
                    next_year["Anticipated FY Budget"],
                    errors="coerce",
                ).fillna(0).sum()

                st.markdown(
                    f'<div class="premium-note">'
                    f'<strong>{carried_count:,}</strong> request'
                    f'{"s" if carried_count != 1 else ""} are currently positioned for the next budget cycle, '
                    f'with an anticipated planning requirement of <strong>{money_zero(planning_total)}</strong>. '
                    f'Before FY 2028-29 is finalized, each item should be revalidated, repriced, and either funded, '
                    f'elevated, or closed.</div>',
                    unsafe_allow_html=True,
                )

        dataframe_download(
            filtered_deferred,
            "korbi_deferred_future_needs.csv",
            "Download Deferred & Future Needs CSV",
        )


# ============================================================
# DECISION LOG
# ============================================================

elif page == "Decision Log":

    section_title(
        "Decision Log",
        "Management audit trail with the financial rationale and requestor-ready response saved at the time of decision."
    )

    current_decisions = current_decision_df()

    if current_decisions.empty:
        st.info("No management decisions have been recorded yet. Approve, defer, or deny a Purchase Request to populate this page.")
    else:
        if "manager_decision" in current_decisions.columns:
            counts = current_decisions["manager_decision"].astype(str).str.upper().value_counts().to_dict()
        else:
            counts = {}

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Approved", counts.get("APPROVE", 0))
        d2.metric("Deferred", counts.get("DEFER", 0))
        d3.metric("Denied", counts.get("DENY", 0))
        d4.metric("Total Decisions", len(current_decisions))

        f1, f2 = st.columns(2)
        with f1:
            program_options = ["All Programs"]
            if "program_name" in current_decisions.columns:
                program_options += sorted(current_decisions["program_name"].dropna().astype(str).unique().tolist())
            program_filter = st.selectbox("Program", program_options, key="decision_program_filter")
        with f2:
            decision_filter = st.selectbox(
                "Decision",
                ["All Decisions", "APPROVE", "DEFER", "DENY"],
                key="decision_type_filter",
            )

        filtered = current_decisions.copy()
        if program_filter != "All Programs" and "program_name" in filtered.columns:
            filtered = filtered[filtered["program_name"].astype(str) == program_filter]
        if decision_filter != "All Decisions" and "manager_decision" in filtered.columns:
            filtered = filtered[filtered["manager_decision"].astype(str).str.upper() == decision_filter]

        summary_cols = [
            c for c in [
                "request_id", "requestor_name", "program_name", "description",
                "amount", "manager_decision", "reviewed_by", "review_date"
            ] if c in filtered.columns
        ]

        st.markdown("## Decision History")
        summary = filtered[summary_cols].copy()
        if "amount" in summary.columns:
            summary["amount"] = summary["amount"].apply(money)
        st.markdown(
            '<div class="korbi-table-wrap">' + summary.to_html(index=False, classes="korbi-table", border=0, escape=True) + '</div>',
            unsafe_allow_html=True,
        )

        if not filtered.empty:
            labels = [
                f"{r.get('request_id', '')} — {r.get('program_name', '')} — {r.get('manager_decision', '')} — {r.get('description', '')}"
                for _, r in filtered.iterrows()
            ]
            chosen = st.selectbox("Open decision", labels)
            record = filtered.iloc[labels.index(chosen)].to_dict()
            decision_value = str(record.get("manager_decision", "")).upper()

            badge_class = {
                "APPROVE": "decision-approve",
                "DEFER": "decision-defer",
                "DENY": "decision-deny",
            }.get(decision_value, "decision-defer")

            st.markdown(
                f'''<span class="decision-badge {badge_class}">{decision_value}</span>''',
                unsafe_allow_html=True,
            )
            st.markdown(f"### {record.get('program_name', '')} — {record.get('description', '')}")

            i1, i2, i3, i4 = st.columns(4)
            i1.metric("Request", money(record.get("amount")))
            i2.metric("Requestor", str(record.get("requestor_name", "")) or "Not provided")
            i3.metric("Reviewer", str(record.get("reviewed_by", "")))
            i4.metric("Decision Date", str(record.get("review_date", "")))

            left, right = st.columns(2, gap="large")
            with left:
                st.markdown("### KORBI Decision Rationale")
                rationale = str(record.get("decision_rationale", "")).strip()
                if not rationale or rationale.lower() == "nan":
                    rationale = str(record.get("budget_impact_summary", ""))
                st.info(rationale)

                st.markdown("### Financial Position at Decision")
                st.write(f"**Before:** {pct(record.get('baseline_percent'))} utilized | {money(record.get('baseline_remaining'))} remaining")
                st.write(f"**After request:** {pct(record.get('percent_with_request'))} utilized | {money(record.get('remaining_with_request'))} remaining")
                if str(record.get("manager_notes", "")).strip() and str(record.get("manager_notes", "")).lower() != "nan":
                    st.write(f"**Manager notes:** {record.get('manager_notes')}")

                if decision_value == "DEFER":
                    next_action_value = str(record.get("next_action", "")).strip()
                    target_fy_value = str(record.get("target_fiscal_year", "")).strip()
                    anticipated_value = safe_float(record.get("anticipated_next_year_budget"))

                    if next_action_value and next_action_value.lower() != "nan":
                        st.write(f"**Next action:** {next_action_value}")
                    if target_fy_value and target_fy_value.lower() != "nan":
                        st.write(f"**Planning target:** {target_fy_value}")
                    if anticipated_value > 0:
                        st.write(f"**Anticipated future-year budget:** {money(anticipated_value)}")

            with right:
                st.markdown("### Email-Ready Response")
                email_text = str(record.get("requestor_email_response", "")).strip()
                if not email_text or email_text.lower() == "nan":
                    email_text = "This decision predates the V7.6 email-response field. Re-save the request decision to generate an email-ready response."
                st.caption("The full response is shown below and wraps vertically for easy reading.")
                wrapped_email_box(email_text)
                st.download_button(
                    "Download Response as TXT",
                    data=email_text.encode("utf-8"),
                    file_name=f"{record.get('request_id', 'korbi')}_response.txt",
                    mime="text/plain",
                    width="stretch",
                )

        dataframe_download(
            current_decisions,
            "korbi_decision_log.csv",
            "Download Decision Log CSV",
        )


# ============================================================
# SYSTEM DATA
# ============================================================

elif page == "System Data":

    section_title(
        "System Data",
        "Dataset status for the current KORBI simulation."
    )

    status_rows = []
    for key, path in FILES.items():
        status_rows.append({
            "Dataset": key,
            "Loaded": path.exists(),
            "File": path.name,
            "Path": str(path),
        })

    st.dataframe(
        pd.DataFrame(status_rows),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        f"Project folder: {PROJECT_FOLDER}"
    )
