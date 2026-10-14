
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
        --ssu-blue: #004C97;
        --ssu-light: #ABCAE9;
        --ssu-navy: #17365D;
        --ssu-bg: #F5F8FC;
        --ssu-border: #D5E2F0;
        --ssu-text: #26384A;
        --ssu-muted: #64788A;
        --good: #2E7D32;
        --warn: #9A6B00;
        --risk: #C75A00;
        --bad: #B3261E;
    }

    .stApp { background: var(--ssu-bg); }
    .block-container {
        max-width: 1500px !important;
        padding-top: 4.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003B78 0%, #004C97 58%, #17365D 100%);
    }

    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        color: #17365D !important;
        background: #FFFFFF !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: .35rem .45rem;
        border-radius: 8px;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,.14);
    }

    .korbi-header {
        background: linear-gradient(135deg, #004C97 0%, #17365D 100%);
        border-bottom: 5px solid #ABCAE9;
        border-radius: 0 0 18px 18px;
        padding: 1.25rem 1.5rem 1rem;
        margin: -.95rem -1rem 1.2rem;
        box-shadow: 0 4px 14px rgba(0, 76, 151, .12);
    }

    .korbi-title {
        font-size: 2.6rem;
        font-weight: 900;
        color: #FFFFFF !important;
        line-height: 1;
    }

    .korbi-subtitle {
        margin-top: .45rem;
        color: #DDEBFA !important;
        font-size: .95rem;
    }

    .korbi-brandline {
        margin-top: .55rem;
        color: #ABCAE9 !important;
        font-size: .8rem;
        font-weight: 800;
        letter-spacing: .08rem;
        text-transform: uppercase;
    }

    h1, h2, h3, h4, h5, h6 { color: var(--ssu-navy) !important; }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-top: 4px solid var(--ssu-blue);
        border-radius: 12px;
        padding: .7rem .85rem;
        box-shadow: 0 3px 10px rgba(23,54,93,.05);
    }

    [data-testid="stMetric"] * { color: var(--ssu-navy) !important; }

    .hero {
        background: linear-gradient(118deg, #102C49 0%, #004C97 100%);
        border-radius: 18px;
        padding: 3.4rem 3.5rem;
        margin: .2rem 0 1.25rem;
        box-shadow: 0 10px 28px rgba(7,35,63,.12);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.08);
    }

    .hero-inner {
        position: relative;
        z-index: 2;
        max-width: 1050px;
    }

    .hero-kicker {
        color: #ABCAE9 !important;
        font-size: .78rem;
        font-weight: 900;
        letter-spacing: .16rem;
        text-transform: uppercase;
    }

    .hero-title {
        color: #FFFFFF !important;
        font-size: clamp(4.2rem, 7vw, 6.5rem);
        font-weight: 900;
        line-height: .9;
        letter-spacing: -.16rem;
        margin: .85rem 0 1.1rem;
    }

    .hero-sub {
        color: #FFFFFF !important;
        font-size: clamp(1.45rem, 2.2vw, 2rem);
        font-weight: 750;
        line-height: 1.14;
        max-width: 900px;
    }

    .hero-body {
        color: #D8E7F5 !important;
        max-width: 900px;
        font-size: 1.08rem;
        line-height: 1.68;
        margin-top: 1.2rem;
    }

    .value-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .85rem;
        margin: 0 0 1.8rem;
    }

    .value-card {
        background: #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-top: 3px solid var(--ssu-blue);
        border-radius: 10px;
        padding: 1.15rem 1.2rem;
        box-shadow: 0 3px 10px rgba(7,35,63,.04);
    }

    .value-card .num {
        color: var(--ssu-blue) !important;
        font-weight: 900;
        font-size: .72rem;
        letter-spacing: .12rem;
    }

    .value-card h3 {
        margin: .45rem 0 .5rem;
        font-size: 1.05rem;
    }

    .value-card p {
        margin: 0;
        color: var(--ssu-muted) !important;
        line-height: 1.55;
        font-size: .9rem;
    }

    .landing-panel {
        background: #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-radius: 18px;
        padding: 1.6rem 1.75rem;
        box-shadow: 0 5px 18px rgba(7,35,63,.05);
        margin-bottom: 1rem;
    }

    .capability-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem 1.2rem;
        margin: .7rem 0 1.8rem;
    }

    .capability-card {
        background: #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-top: 3px solid var(--ssu-blue);
        border-radius: 10px;
        padding: 1.05rem 1.1rem;
        box-shadow: 0 3px 10px rgba(7,35,63,.04);
    }

    .capability-card h3 {
        margin: 0 0 .45rem 0;
        color: #17365D !important;
        -webkit-text-fill-color: #17365D !important;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .capability-card p {
        margin: 0;
        color: #263746 !important;
        -webkit-text-fill-color: #263746 !important;
        opacity: 1 !important;
        line-height: 1.55;
        font-size: .9rem;
        font-weight: 600;
    }

    .landing-eyebrow {
        color: var(--ssu-blue) !important;
        font-size: .72rem;
        font-weight: 900;
        letter-spacing: .12rem;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }

    .landing-panel h2 {
        margin: 0 0 .65rem;
        font-size: 1.55rem;
    }

    .landing-panel p {
        color: var(--ssu-muted) !important;
        line-height: 1.65;
        margin: 0;
    }

    @media (max-width: 900px) {
        .value-grid { grid-template-columns: repeat(2, 1fr); }
        .hero { padding: 2.7rem 2rem; }
        .hero-title { letter-spacing: -.08rem; }
    }

    .support-card {
        background: linear-gradient(135deg,#17365D 0%,#004C97 100%);
        border-radius: 18px;
        padding: 1.6rem 2rem;
        margin: .75rem 0 1.2rem;
        box-shadow: 0 6px 18px rgba(23,54,93,.12);
    }

    .support-kicker {
        color: #ABCAE9 !important;
        text-transform: uppercase;
        letter-spacing: .1rem;
        font-size: .78rem;
        font-weight: 850;
    }

    .support-value {
        color: #FFFFFF !important;
        font-size: 3rem;
        font-weight: 950;
        margin-top: .25rem;
    }

    .support-copy {
        color: #DDEBFA !important;
        margin-top: .4rem;
        font-size: 1rem;
    }

    .analysis-box {
        background: #FFFFFF;
        border: 1px solid var(--ssu-border);
        border-left: 5px solid var(--ssu-blue);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin: .55rem 0 1rem;
    }

    .small-muted { color: var(--ssu-muted); font-size: .85rem; }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--ssu-border);
        border-radius: 10px;
        overflow: hidden;
        background: #FFFFFF;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 700;
    }

    .stButton > button[kind="primary"] {
        background: var(--ssu-blue) !important;
        border-color: var(--ssu-blue) !important;
        color: #FFFFFF !important;
    }

    /* V7.5 operational status cards */
    .program-grid {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:.75rem;
        margin:.5rem 0 1.5rem 0;
    }
    .program-card {
        border:1px solid var(--ssu-border);
        border-left:5px solid #1565C0;
        border-radius:12px;
        padding:.85rem .95rem;
        background:#EAF2FB;
        min-height:92px;
    }
    .program-card .sport {font-size:.74rem;font-weight:850;text-transform:uppercase;letter-spacing:.02rem;}
    .program-card .status {font-size:1.18rem;font-weight:900;margin:.12rem 0 .2rem;}
    .program-card .detail {font-size:.82rem;line-height:1.25;color:#334E68 !important;}
    .program-card.healthy {background:#EAF6EC;border-left-color:#2E7D32;}
    .program-card.healthy .sport,.program-card.healthy .status {color:#2E7D32 !important;}
    .program-card.monitor {background:#EAF2FB;border-left-color:#1565C0;}
    .program-card.monitor .sport,.program-card.monitor .status {color:#1565C0 !important;}
    .program-card.caution {background:#FFF7DA;border-left-color:#B07A00;}
    .program-card.caution .sport,.program-card.caution .status {color:#9A6B00 !important;}
    .program-card.highrisk {background:#FFF0E5;border-left-color:#C75A00;}
    .program-card.highrisk .sport,.program-card.highrisk .status {color:#C75A00 !important;}
    .program-card.overbudget {background:#FDECEA;border-left-color:#B3261E;}
    .program-card.overbudget .sport,.program-card.overbudget .status {color:#B3261E !important;}

    .section-card {
        background:#FFFFFF;
        border:1px solid var(--ssu-border);
        border-top:4px solid var(--ssu-blue);
        border-radius:12px;
        padding:1rem 1.05rem;
        box-shadow:0 2px 8px rgba(23,54,93,.04);
        height:100%;
    }
    .section-card .eyebrow {font-size:.72rem;font-weight:850;text-transform:uppercase;letter-spacing:.05rem;color:#64788A !important;}
    .section-card .big {font-size:1.7rem;font-weight:900;color:#17365D !important;margin:.15rem 0;}
    .decision-badge {display:inline-block;padding:.28rem .55rem;border-radius:999px;font-size:.72rem;font-weight:900;letter-spacing:.04rem;}
    .decision-approve {background:#EAF6EC;color:#2E7D32 !important;}
    .decision-defer {background:#FFF7DA;color:#8A6200 !important;}
    .decision-deny {background:#FDECEA;color:#B3261E !important;}

    .korbi-table-wrap {
        overflow-x:auto;
        background:#FFFFFF;
        border:1px solid var(--ssu-border);
        border-radius:12px;
        margin:.5rem 0 1.25rem;
        box-shadow:0 2px 8px rgba(23,54,93,.04);
    }
    table.korbi-table {border-collapse:collapse;width:100%;min-width:760px;font-size:.84rem;}
    .korbi-table th {background:#17365D;color:#FFFFFF !important;text-align:left;padding:.72rem .75rem;white-space:nowrap;}
    .korbi-table td {padding:.65rem .75rem;border-bottom:1px solid #E2EAF2;color:#26384A !important;white-space:nowrap;}
    .korbi-table tr:nth-child(even) td {background:#F7FAFD;}
    .korbi-table tr:hover td {background:#EAF2FB;}
    .korbi-table .yes {color:#2E7D32 !important;font-weight:800;}
    .korbi-table .no {color:#9AA8B6 !important;}

    @media (max-width: 900px) {
        .program-grid {grid-template-columns:1fr;}
        .capability-grid {grid-template-columns:1fr;}
    }

    /* =====================================================
       V7.5 LIGHT-BACKGROUND TEXT SAFETY
       White text is reserved for intentionally dark surfaces.
       ===================================================== */

    /* Standard light-page text */
    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] .stCaption,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] {
        color:#263746;
    }

    /* Landing / content cards */
    .value-card,
    .value-card *,
    .capability-card,
    .capability-card *,
    .landing-panel,
    .landing-panel *,
    .analysis-box,
    .analysis-box *,
    .section-card,
    .section-card * {
        color:#263746 !important;
        -webkit-text-fill-color:#263746 !important;
        opacity:1 !important;
    }

    .value-card h3,
    .capability-card h3,
    .landing-panel h2,
    .section-card .big {
        color:#17365D !important;
        -webkit-text-fill-color:#17365D !important;
        font-weight:800 !important;
    }

    .value-card .num,
    .landing-eyebrow {
        color:#00539B !important;
        -webkit-text-fill-color:#00539B !important;
        font-weight:900 !important;
    }

    .value-card p,
    .capability-card p,
    .landing-panel p {
        color:#263746 !important;
        -webkit-text-fill-color:#263746 !important;
        opacity:1 !important;
        font-weight:600 !important;
    }

    /* Streamlit tabs on light backgrounds */
    button[data-baseweb="tab"] {
        background:transparent !important;
        color:#17365D !important;
        -webkit-text-fill-color:#17365D !important;
        font-weight:700 !important;
    }

    button[data-baseweb="tab"] *,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] div {
        color:#17365D !important;
        -webkit-text-fill-color:#17365D !important;
        opacity:1 !important;
        font-weight:700 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"],
    button[data-baseweb="tab"][aria-selected="true"] * {
        color:#00539B !important;
        -webkit-text-fill-color:#00539B !important;
        font-weight:850 !important;
    }

    /* Explicitly preserve white text only on dark surfaces */
    .hero-title,
    .hero-sub,
    .support-value,
    .korbi-table th,
    .stButton > button[kind="primary"] {
        color:#FFFFFF !important;
        -webkit-text-fill-color:#FFFFFF !important;
    }

    .hero-body {
        color:#D8E7F5 !important;
        -webkit-text-fill-color:#D8E7F5 !important;
    }

    .hero-kicker,
    .support-kicker {
        color:#ABCAE9 !important;
        -webkit-text-fill-color:#ABCAE9 !important;
    }

    .support-copy {
        color:#DDEBFA !important;
        -webkit-text-fill-color:#DDEBFA !important;
    }

    /* Email-ready response boxes: vertical wrapping, never horizontal scroll */
    .email-response-box {
        width: 100% !important;
        box-sizing: border-box !important;
        background: #171A21 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #2B3440 !important;
        border-radius: 8px !important;
        padding: 1rem 1.1rem !important;
        margin: .35rem 0 .8rem 0 !important;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace !important;
        font-size: .9rem !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
        overflow-x: hidden !important;
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


def first_existing_column(df, candidates):
    for col in candidates:
        if col in df.columns:
            return col
    return None


def section_title(title, subtitle=None):
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


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


def decision_rationale(row, decision):
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
        return (
            f"The {money(amount)} request for {description} was deferred because approving it now would move "
            f"{program} from {before_pct:.1f}% to {after_pct:.1f}% projected utilization and reduce projected "
            f"year-end flexibility from {money(before_remaining)} to {money(after_remaining)}. The need may be valid, "
            f"but preserving capacity for remaining travel, equipment, and other operating requirements is the stronger "
            f"financial decision at this point. The request can be reconsidered if savings, another funding source, or "
            f"additional budget capacity is identified."
        )

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


def requestor_email(row, decision, name="", notes=""):
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
            f"operating needs. If offsetting savings, another funding source, or additional capacity becomes available, "
            f"we can revisit the request."
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


def save_decision(row, recommendation, suggestion, decision, reviewer, notes, requestor=""):
    decisions = load_decisions()
    rationale = decision_rationale(row, decision)
    email_text = requestor_email(row, decision, requestor, notes)

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
    }

    decisions[str(row.get("request_id", ""))] = record
    write_decisions(list(decisions.values()))
    return record


def department_financial_summary():
    annual = actual = committed = projected = 0.0

    if not department_df.empty:
        if "annual_budget" in department_df.columns:
            annual = pd.to_numeric(department_df["annual_budget"], errors="coerce").fillna(0).sum()
        if "q1_actual" in department_df.columns:
            actual = pd.to_numeric(department_df["q1_actual"], errors="coerce").fillna(0).sum()
        if "open_commitments" in department_df.columns:
            committed = pd.to_numeric(department_df["open_commitments"], errors="coerce").fillna(0).sum()
        if "projected_year_end" in department_df.columns:
            projected = pd.to_numeric(department_df["projected_year_end"], errors="coerce").fillna(0).sum()

    approved_adjustment = approved_decision_adjustments()
    committed += approved_adjustment
    projected += approved_adjustment

    remaining_forecast = max(projected - actual - committed, 0)
    variance = annual - projected

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "approved_decision_adjustment": approved_adjustment,
        "remaining_forecast": remaining_forecast,
        "projected": projected,
        "variance": variance,
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
        # Deferred items remain active and visible as open work.
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


def monthly_financial_outlook(program_name=None):
    months = pd.date_range("2027-07-01", "2028-06-01", freq="MS")

    monthly = pd.DataFrame({"month_date": months})
    monthly["Month"] = monthly["month_date"].dt.strftime("%b %Y")
    monthly["Actual"] = 0.0
    monthly["Committed"] = 0.0
    monthly["Remaining Forecast"] = 0.0

    if not ledger_df.empty:
        date_col = first_existing_column(
            ledger_df, ["transaction_date", "posting_date", "expense_date", "date"]
        )
        amount_col = first_existing_column(
            ledger_df, ["amount", "transaction_amount", "expense_amount", "actual_amount"]
        )
        program_col = first_existing_column(
            ledger_df, ["program_name", "program", "sport", "team"]
        )
        type_col = first_existing_column(
            ledger_df, ["transaction_type", "type", "status"]
        )

        if date_col and amount_col:
            ledger = ledger_df.copy()

            if (
                program_name
                and program_name != "Entire Athletics"
                and program_col
            ):
                ledger = ledger[
                    ledger[program_col].astype(str) == str(program_name)
                ].copy()

            ledger["_date"] = pd.to_datetime(ledger[date_col], errors="coerce")
            ledger["_amount"] = pd.to_numeric(ledger[amount_col], errors="coerce").fillna(0)
            ledger = ledger[ledger["_date"].notna()].copy()
            ledger["month_date"] = ledger["_date"].dt.to_period("M").dt.to_timestamp()

            if type_col:
                committed_mask = ledger[type_col].astype(str).str.contains(
                    "PO|OPEN|COMMIT", case=False, na=False, regex=True
                )
            else:
                committed_mask = pd.Series(False, index=ledger.index)

            actual_group = (
                ledger.loc[~committed_mask]
                .groupby("month_date")["_amount"]
                .sum()
                .to_dict()
            )

            committed_group = (
                ledger.loc[committed_mask]
                .groupby("month_date")["_amount"]
                .sum()
                .to_dict()
            )

            monthly["Actual"] = monthly["month_date"].map(actual_group).fillna(0)
            monthly["Committed"] = monthly["month_date"].map(committed_group).fillna(0)

    if not future_df.empty:
        future_date_col = first_existing_column(
            future_df, ["expense_date", "expected_date", "scheduled_date", "date", "transaction_date"]
        )
        future_amount_col = first_existing_column(
            future_df, ["amount", "expected_amount", "forecast_amount", "expense_amount"]
        )
        future_program_col = first_existing_column(
            future_df, ["program_name", "program", "sport", "team"]
        )

        if future_date_col and future_amount_col:
            future = future_df.copy()

            if (
                program_name
                and program_name != "Entire Athletics"
                and future_program_col
            ):
                future = future[
                    future[future_program_col].astype(str) == str(program_name)
                ].copy()

            future["_date"] = pd.to_datetime(future[future_date_col], errors="coerce")
            future["_amount"] = pd.to_numeric(future[future_amount_col], errors="coerce").fillna(0)
            future = future[future["_date"].notna()].copy()
            future["month_date"] = future["_date"].dt.to_period("M").dt.to_timestamp()

            future_group = future.groupby("month_date")["_amount"].sum().to_dict()
            monthly["Remaining Forecast"] = monthly["month_date"].map(future_group).fillna(0)

    monthly["Monthly Outlook"] = (
        monthly["Actual"] + monthly["Committed"] + monthly["Remaining Forecast"]
    )

    simulation_month = pd.Timestamp(SIMULATION_DATE).to_period("M").to_timestamp()
    monthly["Status"] = monthly["month_date"].apply(
        lambda x: "EXECUTED" if x < simulation_month else ("CURRENT" if x == simulation_month else "FORECAST")
    )

    return monthly[
        ["Month", "Status", "Actual", "Committed", "Remaining Forecast", "Monthly Outlook"]
    ]


def program_metrics(program_name):
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
    remaining = safe_float(row.get("baseline_remaining"))

    approved_adjustment = approved_decision_adjustments(program_name)
    committed += approved_adjustment
    projected += approved_adjustment
    remaining = annual - projected
    utilization = (projected / annual * 100) if annual else 0.0
    unallocated = annual - actual - committed

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "approved_decision_adjustment": approved_adjustment,
        "unallocated": unallocated,
        "projected": projected,
        "remaining": remaining,
        "utilization": utilization,
    }


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def go_to_page(page_name):
    st.session_state["page_nav"] = page_name


if "page_nav" not in st.session_state:
    st.session_state["page_nav"] = "Home"


st.sidebar.markdown("## KORBI")
st.sidebar.caption("Sonoma State Athletics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Executive Dashboard",
        "Monthly Financials",
        "Sport Budgets",
        "Purchase Requests",
        "CSU Benchmarking",
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
    st.info(
        "V7.5 simulation environment — financial position as of October 1, 2027. "
        "Simulated activity is not Sonoma State actual financial data."
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
                    <div class="hero-kicker">V7.5 Simulation Environment • Fall 2027 Restart Scenario</div>
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
            width="stretch",
            on_click=go_to_page,
            args=("Sport Budgets",),
        )

    with launch3:
        st.button(
            "Review Purchase Requests",
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
        "Department-wide financial position, university support requirement, risk, and management workload."
    )

    support = university_support_projection()

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
        "External / earned revenue remains separate from university support. In this simulation, each additional "
        "dollar of outside athletics revenue reduces the modeled university requirement dollar-for-dollar if expenses "
        "remain unchanged."
    )

    st.markdown("## Projected Year-End Position")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Actual Posted", compact_money(support["actual"]))
    f2.metric("Approved / Committed", compact_money(support["committed"]))
    f3.metric("Remaining Forecast", compact_money(support["remaining_forecast"]))
    f4.metric("Projected Year-End", compact_money(support["projected"]))

    if support.get("approved_decision_adjustment", 0) > 0:
        st.caption(
            f"Saved purchase approvals currently add {money(support['approved_decision_adjustment'])} to the "
            "simulation's committed and projected year-end expense position."
        )
    else:
        st.caption("Actual Posted + Approved / Committed + Remaining Forecast = Projected Year-End.")

    if support["variance"] >= 0:
        st.markdown(
            f"""
            <div style="
                background:#DDF3E7;
                color:#18794E;
                border:1px solid #B7E2CB;
                border-left:4px solid #18794E;
                border-radius:8px;
                padding:14px 16px;
                margin:14px 0 22px 0;
                font-size:15px;
                font-weight:700;
            ">
                KORBI currently projects Athletics to finish
                {money(support['variance'])} favorable to the annual plan.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="
                background:#FCE8E6;
                color:#B42318;
                border:1px solid #F5C2BE;
                border-left:4px solid #B42318;
                border-radius:8px;
                padding:14px 16px;
                margin:14px 0 22px 0;
                font-size:15px;
                font-weight:700;
            ">
                KORBI currently projects Athletics to finish
                {money(abs(support['variance']))} over the annual plan.
            </div>
            """,
            unsafe_allow_html=True,
        )

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

    st.markdown("## Program Budget Status — All 10 Restart Sports")

    cards = []
    if not triage_df.empty and "program_name" in triage_df.columns:
        for program_name in sorted(triage_df["program_name"].dropna().astype(str).unique()):
            metrics = program_metrics(program_name)
            if not metrics:
                continue

            util = metrics["utilization"]
            if util > 100:
                status, css = "OVER BUDGET", "overbudget"
            elif util >= 95:
                status, css = "HIGH RISK", "highrisk"
            elif util >= 90:
                status, css = "CAUTION", "caution"
            elif util >= 80:
                status, css = "MONITOR", "monitor"
            else:
                status, css = "HEALTHY", "healthy"

            cards.append(
                f'''<div class="program-card {css}">
                    <div class="sport">{program_name}</div>
                    <div class="status">{status}</div>
                    <div class="detail">{util:.1f}% projected utilization | Remaining capacity: {money(metrics["remaining"])}</div>
                </div>'''
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
    d2.metric("YTD Actual Expenditures", money(support["actual"]))
    d3.metric("Projected Year-End", money(support["projected"]))
    d4.metric(
        "Projected Favorable Variance" if support["variance"] >= 0 else "Projected Unfavorable Variance",
        money(abs(support["variance"])),
    )

    util = (support["projected"] / support["annual"] * 100) if support["annual"] else 0
    st.progress(min(max(util / 100, 0), 1.0), text=f"Department projected utilization: {util:.1f}%")

    st.markdown("## KORBI Executive Interpretation")
    st.info(
        "KORBI keeps the department focused on four connected questions: what has posted, what has already been "
        "committed, what is still forecasted, and how much university support will ultimately be required after "
        "external athletics revenue is considered."
    )


# ============================================================
# MONTHLY FINANCIALS
# ============================================================

elif page == "Monthly Financials":

    section_title(
        "Monthly Financials",
        "Executed months, current commitments, and remaining forecast through the end of FY 2027-28."
    )

    sport_options = ["Entire Athletics"]

    if not triage_df.empty and "program_name" in triage_df.columns:
        sport_options += sorted(
            triage_df["program_name"].dropna().astype(str).unique().tolist()
        )

    scope = st.selectbox("View", sport_options)

    monthly_outlook = monthly_financial_outlook(scope)

    if monthly_outlook.empty:
        st.info("No monthly transaction or forecast data is currently available.")
    else:
        st.markdown("### FY 2027-28 Monthly Execution & Forecast")

        st.dataframe(
            accounting_table(
                monthly_outlook,
                currency_cols=[
                    "Actual",
                    "Committed",
                    "Remaining Forecast",
                    "Monthly Outlook",
                ],
            ),
            width="stretch",
            hide_index=True,
        )

        executed_total = monthly_outlook.loc[
            monthly_outlook["Status"] == "EXECUTED", "Actual"
        ].sum()

        current_and_future_commitments = monthly_outlook["Committed"].sum()
        future_total = monthly_outlook["Remaining Forecast"].sum()
        outlook_total = monthly_outlook["Monthly Outlook"].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Executed Actuals", money(executed_total))
        m2.metric("Open / Committed", money(current_and_future_commitments))
        m3.metric("Future Forecast", money(future_total))
        m4.metric("Modeled FY Outlook", money(outlook_total))

        st.info(
            "As each month closes, KORBI replaces forecast assumptions with actual posted activity. "
            "That makes the year-end view more reliable as the fiscal year progresses."
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
        "Program budgets, actuals, commitments, year-end forecast, and request status."
    )

    if triage_df.empty or "program_name" not in triage_df.columns:
        st.warning("Sport-level triage/budget data is not loaded.")
    else:
        programs = sorted(triage_df["program_name"].dropna().astype(str).unique())
        selection = st.selectbox("Program", programs)
        metrics = program_metrics(selection)

        if metrics:
            b1, b2, b3, b4, b5 = st.columns(5)
            b1.metric("Annual Budget", compact_money(metrics["annual"]))
            b2.metric("Actual Spend", compact_money(metrics["actual"]))
            b3.metric("Committed", compact_money(metrics["committed"]))
            b4.metric("Projected Year-End", compact_money(metrics["projected"]))
            b5.metric("Projected Remaining", compact_money(metrics["remaining"]))

            st.progress(
                min(max(metrics["utilization"] / 100, 0), 1.0),
                text=f"Projected utilization: {metrics['utilization']:.1f}%"
            )

            if metrics["utilization"] > 100:
                st.error("KORBI classifies this program as OVER BUDGET.")
            elif metrics["utilization"] >= 95:
                st.error("KORBI classifies this program as HIGH RISK.")
            elif metrics["utilization"] >= 90:
                st.warning("KORBI classifies this program as CAUTION.")
            elif metrics["utilization"] >= 80:
                st.info("KORBI classifies this program as MONITOR.")
            else:
                st.success("KORBI classifies this program as HEALTHY.")

            if metrics.get("approved_decision_adjustment", 0) > 0:
                st.caption(
                    f"Saved approvals add {money(metrics['approved_decision_adjustment'])} to this program's current "
                    "committed and projected year-end position."
                )

        request_view = request_status_table(selection)
        st.markdown("## Request Center")

        if request_view.empty:
            st.info(f"No requests are currently loaded for {selection}.")
        else:
            open_count = int((request_view["request_status"] == "OPEN").sum())
            allocated_count = int((request_view["request_type"] == "ALLOCATED").sum())
            approved_count = int((request_view["request_status"] == "APPROVED").sum())
            denied_count = int((request_view["request_status"] == "DENIED").sum())

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Open Requests", open_count)
            r2.metric("Allocated / Planned", allocated_count)
            r3.metric("Approved", approved_count)
            r4.metric("Denied", denied_count)

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
                    "Allocated / Planned is a request type, not an approval. A planned item still follows the same "
                    "review and purchasing controls."
                )

            with approved_tab:
                approved_rows = request_view[request_view["request_status"] == "APPROVED"]
                show_request_rows(approved_rows, f"No approved requests for {selection}.")
                if not approved_rows.empty:
                    approved_value = pd.to_numeric(approved_rows["amount"], errors="coerce").fillna(0).sum()
                    st.metric("Approved Request Value", money(approved_value))
                    st.caption(
                        "Approved requests are treated as committed money in KORBI's live simulation even before the "
                        "final invoice posts."
                    )

            with denied_tab:
                show_request_rows(
                    request_view[request_view["request_status"] == "DENIED"],
                    f"No denied requests for {selection}."
                )

        st.markdown("## Coach Financial Impact")
        if metrics:
            st.info(
                f"{selection} currently has {money(metrics['remaining'])} of projected year-end financial flexibility. "
                "A new request may fit within today's budget while still reducing the program's ability to respond to "
                "travel changes, equipment needs, or other unexpected requirements later. KORBI shows the tradeoff "
                "without assuming what the coach may want to buy next."
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

    mode = st.segmented_control(
        "Show",
        options=[
            "Awaiting Review",
            "All Requests",
            "Reviewed",
        ],
        default="Awaiting Review",
        selection_mode="single",
    )

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
    st.write(suggestion)

    st.markdown("#### Coach Impact")
    st.info(coach_impact(row))

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
    st.write(budget_impact(row))

    st.markdown("#### Risk")
    st.write(risk_summary(row))

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

    notes = st.text_area(
        "Manager notes",
        value=str(raw_row.get("manager_notes", "")) if str(raw_row.get("manager_notes", "")).lower() != "nan" else "",
        placeholder="Optional context, conditions, offsets, or follow-up instructions.",
        key=f"notes_{row.get('request_id', '')}",
    )

    # Preview the exact rationale that will be stored with the decision.
    rationale_preview = decision_rationale(row, decision)
    email_preview = requestor_email(row, decision, requestor, notes)

    st.markdown("### KORBI Decision Explanation")
    st.info(rationale_preview)

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

            st.caption(
                f"Closest total-spend comparator: {closest.get('School', '')} at {money(closest.get('Total Expense'))}. "
                f"Peer-average expense per athlete is approximately {money(peer_avg_epa)}."
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

            with right:
                st.markdown("### Email-Ready Response")
                email_text = str(record.get("requestor_email_response", "")).strip()
                if not email_text or email_text.lower() == "nan":
                    email_text = "This decision predates the V7.5 email-response field. Re-save the request decision to generate an email-ready response."
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
