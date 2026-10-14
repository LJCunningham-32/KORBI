
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
    .sidebar-brand .ssu-office {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: .82rem;
        font-weight: 900;
        letter-spacing: .08rem;
        margin-top: .08rem;
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
        width: 100%;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.55fr) minmax(290px, .7fr);
        gap: 2.2rem;
        align-items: center;
    }

    .hero-copy {
        min-width: 0;
    }

    .hero-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 240px;
        position: relative;
    }

    .hero-logo::before {
        content: "";
        position: absolute;
        width: 115%;
        height: 115%;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(171,202,233,.18) 0%, rgba(171,202,233,.06) 42%, transparent 70%);
        filter: blur(2px);
    }

    .hero-logo img {
        position: relative;
        z-index: 2;
        display: block;
        width: 100%;
        max-width: 440px;
        max-height: 285px;
        object-fit: contain;
        opacity: .78;
        mix-blend-mode: screen;
        filter: saturate(.92) contrast(1.08) drop-shadow(0 12px 24px rgba(0,0,0,.18));
        border-radius: 14px;
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
        .hero-grid {grid-template-columns:1fr;}
        .hero-logo {min-height:160px;}
        .hero-logo img {max-width:360px;max-height:220px;opacity:.72;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# Subtle Seawolves pride watermark using the user-provided Sonoma State image.
_SEAWOLVES_WATERMARK = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5Ojf/2wBDAQoKCg0MDRoPDxo3JR8lNzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzf/wAARCAH6A4QDASIAAhEBAxEB/8QAHAABAAMBAQEBAQAAAAAAAAAAAAUGBwQDAgEI/8QAUhAAAQMDAQMIBQkFBgMGBgMBAQACAwQFEQYSITEHEyJBUWFxgRSRkqHRFRcjMkJSVLHBFjNTYnIkQ1WCleGTlPAlNDVWY6JEg7LS4vFFc8I2/8QAGQEBAAMBAQAAAAAAAAAAAAAAAAECAwQF/8QALBEBAQACAQMEAgIBBAMBAAAAAAECEQMSITEEE0FRFCJhcTJCkbHxI1LwM//aAAwDAQACEQMRAD8AjURF6zzBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQERfhIHEgeakfqL8D2ng4HzX6oBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQERcVxq3xGOnpWmSqmOzGwDJ3qR+XG5w0Q2fryngwHh4r8grKu5Tej2ekfUPH1nkYa1TVNoGOShi9MnJq5JA+eQHOy3flre/vU1bDE/aoLExtPQ052JaloyXu6wztPa4qeyO6Eg0fXz4+VLuInHfzNM3J9a6n6BtgjLnz10rgOAeMn3K2QQRwN2Y24zxJOSfE9a8qypkp2ZipJqh3U2MtH5kKu6nUZpcNF3Rspdb6KUQjgJZ2F59SiKilvNpP9ohqoAOtwJb6+CvF7vF6YwmeejssXUHv52Z3gBlUmsvlyfK5rLrWTMPW8lufLKvNqXT7pb/KzAqWCQfebuKm6Ssgq25geCetp3EeSrcFrras7ZZsB28ufuz5KRprCYnB7qpzXjrjGEuky1NIvxoLWgFxcQOJ61+qiwiIgIi/HODWlziABvJKD9RQ5qJ6q7xxWiQTPkaRzZO5xGTjf14UhRVQqWOBYY5YzsyRu4tKnSNuhERQkREQEREBEXw+WONzWveA55w0Z3lSPtFGVd3jjkENMOelJ2R90FSTA4NG2QXY3kdqaRt+oiKEiIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiIPx7gxjnOOA0ZK/dH05ldNephmWaYU1ID9kni4eAz71xXqQx22YjiQG+sqwWtopo9J0g3B7ZJj3u2Cf1U/CPl165uM1Dao6Oh2vSax3NMDfrBvXj3DzU3aaKO3W2npIm4bFGAe89Z9a9JKSCSriqpIw6aJpaxx+yDxx3ruoWNlrYI3DLXSAH1qly1FpN14eIwuStlro2E0VLDOex82x+ilr0ymtFO99VKHSBpkkkJw2Nv6lZRqDUF0vVLUT0QfS2mI7JfnZMp4AZ689g80471zcTnOm6r41JqK7uqTTOZRQPO4inLZH+BdvwvK3W1sH01R9JUO3lzt+FC2GISXJhd9gF3mrUtL27M537iIiqsIiICIiAuSpgNfcaC27Rayol+kI+6N5XWuczNor3a62UhsUc2y9x4AHdlTEVatG1truk1SwUENM2il2YjGwF2z1HxOCFAassNdNqxsltzHFXHIf1Nc0b9rHcuM10GldQsnotuWjqqYSO2jvftZIPrwr3pq4tvFopqpzxtOGzLj7LhxUWdN2md5pQaSqlNRLRVrOaq4Dh7e3HWF2Lt1dpq6S6mNfa4Y5WFoB+kAyRu6+rGFEXKy6kYyOSSna1jXdJ1O7aLQe0damavdHeOpF4VUVdZ61lJdQ17Jf3NQz6r+4969nOawZe4NA6ycIP1eNXUMpad80nBo4dp7Fzvu1MH7EW3O/siaXL8pJI7ldGc/FI2loonVM0cjcF2zwHrx600bfhuJnZCygZztTMOiz7vaT2YXPW2V8csVVUV3O05p+emqI+G8kBjO0nGF+3Cut0VumntY5upuLsSx9dO0fWaO5x9yiJrlVVFupre52YIHEsaBvJJ6/08VaRW192tzJLvCWsDGlx2W8cbtytar1tt8lPdmRzbpImbcjfuE8Ae/erCoyTiIiKqwiIgIiICIiAiIgIiICIiAiIgIiICIv0AngM+CD8Reraed31YZD4MK9Bb6x3ClmP+QoOZF2C11x/+Fl9lPkuv/Cy+pBxous2yuHGkl9lfDqKrb9ammH+QoOdF9uilb9aN48WlfB3cUBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQcF9btWyXHUQfepeoqhBT6QuGfo24ieezIAP6ri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REQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQf/9k="

st.markdown(
    """
    <style>
    /* Seawolves branding is displayed as a dedicated Home-page panel,
       never underneath working content or financial text. */
    .seawolves-brand-panel {
        background: linear-gradient(135deg, #E7F0F8 0%, #D3E3F1 100%);
        border: 1px solid #C4D8E9;
        border-top: 4px solid #00539B;
        border-radius: 16px;
        padding: 1rem;
        margin: 0 0 1rem 0;
        min-height: 260px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(16,44,73,.08);
    }
    .seawolves-brand-panel img {
        display: block;
        width: 100%;
        height: auto;
        max-height: 330px;
        object-fit: contain;
        border-radius: 11px;
    }
    @media (max-width: 900px) {
        .seawolves-brand-panel {
            min-height: 200px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# BASIC HELPERS
# ============================================================

def safe_financial_html(text):
    """Escape narrative text for HTML while preserving visible dollar signs and line breaks."""
    return (
        html.escape(str(text))
        .replace("$", "&#36;")
        .replace("\n", "<br>")
    )


def wrapped_email_box(text):
    safe_text = safe_financial_html(text)
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
        <div class="ssu-mark">SONOMA STATE ATHLETICS</div>
        <div class="ssu-office">BUSINESS OFFICE</div>
        <div class="ssu-sub">Seawolves · KORBI</div>
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
            f"""
            <div class="hero">
                <div class="hero-inner">
                    <div class="hero-grid">
                        <div class="hero-copy">
                            <div class="hero-kicker">V7.7.3 Athletics Premium • Simulation Environment • Fall 2027 Restart Scenario</div>
                            <div class="hero-title">KORBI</div>
                            <div class="hero-sub">One operating picture for every program, every request, and every dollar.</div>
                            <div class="hero-body">
                                KORBI empowers coaches with financial context, aligns day-to-day decisions with department objectives,
                                standardizes operating procedures, and makes the year-round impact of budget changes clear before
                                decisions are made.
                            </div>
                        </div>
                        <div class="hero-logo">
                            <img src="{_SEAWOLVES_WATERMARK}" alt="Sonoma State Seawolves">
                        </div>
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
        f'<div class="premium-note">{safe_financial_html(str(suggestion))}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Coach Impact")
    st.markdown(
        f'<div class="premium-note">{safe_financial_html(coach_impact(row))}</div>',
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
        f'<div class="neutral-note">{safe_financial_html(budget_impact(row))}</div>',
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
    st.markdown(
        f'<div class="premium-note">{safe_financial_html(rationale_preview)}</div>',
        unsafe_allow_html=True,
    )

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
                st.markdown(
                    f'<div class="premium-note">{safe_financial_html(rationale)}</div>',
                    unsafe_allow_html=True,
                )

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
