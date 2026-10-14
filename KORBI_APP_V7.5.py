
import csv
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

FILES = {
    "triage": PROCESSED_FOLDER / "korbi_bulk_triage_results.csv",
    "decisions": PROCESSED_FOLDER / "korbi_management_decisions.csv",
    "department": PROCESSED_FOLDER / "korbi_department_q1_snapshot.csv",
    "budgets": PROCESSED_FOLDER / "korbi_category_budgets.csv",
    "ledger": PROCESSED_FOLDER / "korbi_operational_ledger.csv",
    "future": PROCESSED_FOLDER / "korbi_future_expenses.csv",
    "funding": PROCESSED_FOLDER / "sonoma_funding_model.csv",
    "staffing": PROCESSED_FOLDER / "sonoma_staffing_model.csv",
    "financial_model": PROCESSED_FOLDER / "sonoma_financial_model_summary.csv",
    "financial_history": PROCESSED_FOLDER / "sonoma_financial_history.csv",
    "proposed_budget": PROCESSED_FOLDER / "sonoma_proposed_athletics_budget.csv",
    "peer_comparison": PROCESSED_FOLDER / "eada_peer_comparison_2024.csv",
    "team_benchmark": PROCESSED_FOLDER / "eada_team_benchmark_2024.csv",
    "cost_drivers": PROCESSED_FOLDER / "eada_cost_drivers_2024.csv",
    "team_summary": PROCESSED_FOLDER / "eada_team_summary_2024.csv",
}

SIMULATION_DATE = "2027-10-01"

DECISION_FIELDS = [
    "request_id",
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
    "reviewed_by",
    "review_date",
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
    .block-container { max-width: 1500px; padding-top: 1rem; padding-bottom: 2rem; }

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
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BASIC HELPERS
# ============================================================

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
    PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(FILES["decisions"], "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DECISION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_decisions():
    return {
        str(r.get("request_id", "")): r
        for r in read_rows(FILES["decisions"])
        if r.get("request_id")
    }


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
decision_df = read_df(FILES["decisions"])
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
    amount = safe_float(row.get("amount"))
    before_remaining = safe_float(row.get("baseline_remaining"))
    after_remaining = safe_float(row.get("remaining_with_request"))
    share = amount / before_remaining * 100 if before_remaining > 0 else 100.0

    if after_remaining < 0:
        return (
            f"This request would use the program's remaining flexibility and create a projected "
            f"deficit of {money(abs(after_remaining))}. The request needs an offset, transfer, "
            f"alternative funding source, or a change in scope."
        )

    return (
        f"This request can be evaluated within the current program budget, but it would reduce "
        f"projected year-end flexibility from {money(before_remaining)} to {money(after_remaining)}. "
        f"That uses about {share:.1f}% of the flexibility currently available. KORBI does not assume "
        f"what the program may need later; it shows the tradeoff so the coach can decide whether this "
        f"expense is worth reducing flexibility for future travel changes, equipment needs, or other "
        f"unplanned requirements."
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


def save_decision(row, recommendation, suggestion, decision, reviewer, notes):
    decisions = load_decisions()

    record = {
        "request_id": row.get("request_id", ""),
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
        "reviewed_by": reviewer,
        "review_date": SIMULATION_DATE,
        "manager_notes": notes,
    }

    decisions[str(row.get("request_id", ""))] = record
    write_decisions(list(decisions.values()))


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

    remaining_forecast = max(projected - actual - committed, 0)
    variance = annual - projected

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
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

    if (
        not decision_df.empty
        and "request_id" in decision_df.columns
        and "request_id" in view.columns
    ):
        decision_cols = [
            c for c in [
                "request_id",
                "manager_decision",
                "review_date",
                "reviewed_by",
                "manager_notes",
            ]
            if c in decision_df.columns
        ]
        view = view.merge(
            decision_df[decision_cols],
            on="request_id",
            how="left",
            suffixes=("", "_decision"),
        )

    def classify_request(row):
        decision = str(row.get("manager_decision", "")).upper().strip()
        if decision == "APPROVE":
            return "APPROVED"
        if decision == "DENY":
            return "DENIED"
        if decision == "DEFER":
            return "OPEN"

        allocation_fields = [
            "request_type",
            "budget_type",
            "allocation_status",
            "funding_status",
            "planned_status",
        ]

        allocation_text = " ".join(
            str(row.get(field, "")) for field in allocation_fields
        ).upper()

        if any(word in allocation_text for word in ["ALLOCATED", "PLANNED", "BUDGETED"]):
            return "ALLOCATED"

        return "OPEN"

    view["request_status"] = view.apply(classify_request, axis=1)
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
    utilization = safe_float(row.get("baseline_percent"))
    unallocated = annual - actual - committed

    return {
        "annual": annual,
        "actual": actual,
        "committed": committed,
        "unallocated": unallocated,
        "projected": projected,
        "remaining": remaining,
        "utilization": utilization,
    }


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

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
        "V7.1 simulation environment — financial position as of October 1, 2027. "
        "Simulated activity is not Sonoma State actual financial data."
    )


# ============================================================
# HOME
# ============================================================

if page == "Home":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-inner">
                <div class="hero-kicker">V7.1 Simulation Environment • Fall 2027 Restart Scenario</div>
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
        """,
        unsafe_allow_html=True,
    )

    launch1, launch2, launch3 = st.columns(3)

    with launch1:
        if st.button("Open Executive Dashboard", type="primary", width="stretch"):
            st.session_state["page_nav"] = "Executive Dashboard"
            st.rerun()

    with launch2:
        if st.button("View Sport Budgets", width="stretch"):
            st.session_state["page_nav"] = "Sport Budgets"
            st.rerun()

    with launch3:
        if st.button("Review Purchase Requests", width="stretch"):
            st.session_state["page_nav"] = "Purchase Requests"
            st.rerun()

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        st.markdown(
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
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
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
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## What KORBI Can Do for Sonoma State")
    st.caption("One operating layer for Athletics")

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown("### Live Financial Picture")
        st.write(
            "See actual spend, approved commitments, open requests, future obligations, external revenue, "
            "and projected year-end position in one place."
        )
        st.markdown("### Startup Readiness")
        st.write(
            "Track the equipment, supplies, facilities, travel, and operating work required to have teams ready for Fall 2027."
        )

    with c2:
        st.markdown("### Coach Budget Visibility")
        st.write(
            "Show each coach what has been spent, what is already committed, what remains, and how a request changes flexibility."
        )
        st.markdown("### Standardized Requests")
        st.write(
            "Use the same request, review, approval, denial, and documentation process across every program."
        )

    with c3:
        st.markdown("### Forecast & University Support")
        st.write(
            "Continuously project year-end expenses and show how outside revenue can reduce the university support required."
        )
        st.markdown("### Accountability")
        st.write(
            "Keep an audit trail of requests, management decisions, financial impact, approvals, denials, and remaining obligations."
        )


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

    s1.metric("Projected Athletics Expenses", money(support["projected"]))
    s2.metric("Student-Fee Support", money(support["student_fees"]))
    s3.metric("External / Earned Revenue", money(support["external_revenue"]))
    s4.metric("University Support Required", money(support["required_support"]))

    st.caption(
        "External / earned revenue includes identified donations, sponsorships, ticketing, fundraising, "
        "camps, partnerships, NCAA/conference distributions, licensing, and other outside athletics revenue. "
        "University support remains separate."
    )

    st.markdown("---")
    st.markdown("## Projected Year-End Position")

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Actual Posted", money(support["actual"]))
    f2.metric("Approved / Committed", money(support["committed"]))
    f3.metric("Remaining Forecast", money(support["remaining_forecast"]))
    f4.metric("Projected Year-End", money(support["projected"]))

    st.caption(
        "Actual Posted + Approved / Committed + Remaining Forecast = Projected Year-End."
    )

    if support["variance"] >= 0:
        st.success(
            f"KORBI currently projects Athletics to finish {money(support['variance'])} favorable "
            "to the annual plan."
        )
    else:
        st.error(
            f"KORBI currently projects Athletics to finish {money(abs(support['variance']))} "
            "over the annual plan."
        )

    if not triage_df.empty:
        pending = int((~triage_df["reviewed"]).sum()) if "reviewed" in triage_df.columns else 0
        reviewed = int(triage_df["reviewed"].sum()) if "reviewed" in triage_df.columns else 0

        high_risk = 0
        if "financial_status" in triage_df.columns:
            high_risk = int(
                triage_df["financial_status"].isin(["HIGH RISK", "OVER BUDGET"]).sum()
            )

        st.markdown("## Management Workload")
        c1, c2, c3 = st.columns(3)
        c1.metric("Requests Awaiting Review", pending)
        c2.metric("Requests Reviewed", reviewed)
        c3.metric("High-Risk Requests", high_risk)

        st.markdown("## Program Financial Position")

        rows = []
        if "program_name" in triage_df.columns:
            for program_name in sorted(triage_df["program_name"].dropna().astype(str).unique()):
                metrics = program_metrics(program_name)
                if not metrics:
                    continue
                rows.append({
                    "Program": program_name,
                    "Annual Budget": metrics["annual"],
                    "Actual": metrics["actual"],
                    "Committed": metrics["committed"],
                    "Currently Unallocated": metrics["unallocated"],
                    "Projected Year-End": metrics["projected"],
                    "Projected Remaining": metrics["remaining"],
                    "Projected Utilization": metrics["utilization"],
                })

        if rows:
            program_df = pd.DataFrame(rows)
            st.dataframe(
                accounting_table(
                    program_df,
                    currency_cols=[
                        "Annual Budget",
                        "Actual",
                        "Committed",
                        "Currently Unallocated",
                        "Projected Year-End",
                        "Projected Remaining",
                    ],
                    percent_cols=["Projected Utilization"],
                ),
                width="stretch",
                hide_index=True,
            )

    st.markdown("## KORBI Executive Interpretation")
    st.info(
        "KORBI is designed to keep three questions visible at the same time: "
        "Are we executing the annual plan? What obligations are already committed? "
        "And how much institutional support will Athletics ultimately require after external revenue is considered?"
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
            b1.metric("Annual Budget", money(metrics["annual"]))
            b2.metric("Actual Spend", money(metrics["actual"]))
            b3.metric("Committed", money(metrics["committed"]))
            b4.metric("Projected Year-End", money(metrics["projected"]))
            b5.metric("Projected Remaining", money(metrics["remaining"]))

            st.progress(
                min(metrics["utilization"] / 100, 1.0),
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

        request_view = request_status_table(selection)

        st.markdown("## Request Center")

        if request_view.empty:
            st.info(f"No requests are currently loaded for {selection}.")
        else:
            status_counts = request_view["request_status"].value_counts().to_dict()

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Open Requests", status_counts.get("OPEN", 0))
            r2.metric("Allocated / Planned", status_counts.get("ALLOCATED", 0))
            r3.metric("Approved", status_counts.get("APPROVED", 0))
            r4.metric("Denied", status_counts.get("DENIED", 0))

            open_tab, allocated_tab, approved_tab, denied_tab = st.tabs(
                [
                    "Open Requests",
                    "Allocated Requests",
                    "Approved Requests",
                    "Denied Requests",
                ]
            )

            request_columns = [
                c for c in [
                    "request_id",
                    "description",
                    "category_code",
                    "priority",
                    "amount",
                    "annual_budget",
                    "baseline_remaining",
                    "remaining_with_request",
                    "request_status",
                    "reviewed_by",
                    "review_date",
                ]
                if c in request_view.columns
            ]

            def show_status(status_name):
                status_df = request_view[
                    request_view["request_status"] == status_name
                ][request_columns].copy()

                if status_df.empty:
                    st.info(f"No {status_name.lower()} requests for {selection}.")
                    return

                st.dataframe(
                    accounting_table(
                        status_df,
                        currency_cols=[
                            "amount",
                            "annual_budget",
                            "baseline_remaining",
                            "remaining_with_request",
                        ],
                    ),
                    width="stretch",
                    hide_index=True,
                )

            with open_tab:
                show_status("OPEN")

            with allocated_tab:
                show_status("ALLOCATED")
                st.caption(
                    "Allocated requests are only classified here when the source data explicitly identifies "
                    "them as planned, budgeted, or allocated."
                )

            with approved_tab:
                show_status("APPROVED")

                approved_value = request_view.loc[
                    request_view["request_status"] == "APPROVED", "amount"
                ].apply(safe_float).sum()

                st.metric("Approved Request Value", money(approved_value))

                st.caption(
                    "Approved requests should be treated as committed funds even if the final invoice has not posted yet."
                )

            with denied_tab:
                show_status("DENIED")

        st.markdown("## Coach Financial Impact")

        if metrics:
            st.info(
                f"{selection} currently has {money(metrics['remaining'])} of projected year-end financial "
                "flexibility. A new request may fit within today's budget while still reducing the program's "
                "ability to respond to travel changes, equipment needs, or other unexpected requirements later."
            )
            st.caption(
                "KORBI does not assume what a coach may want to purchase later. It shows the flexibility being used "
                "so the coach can make the tradeoff with better information."
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

    mode = st.radio(
        "Show",
        ["Awaiting Review", "All Requests", "Reviewed"],
        horizontal=True,
    )

    if mode == "Awaiting Review":
        view_df = triage_df[~triage_df["reviewed"]].copy()
    elif mode == "Reviewed":
        view_df = triage_df[triage_df["reviewed"]].copy()
    else:
        view_df = triage_df.copy()

    if view_df.empty:
        st.success("No requests in this view.")
        st.stop()

    labels = [
        f"{r.get('request_id', '')} — {r.get('program_name', '')} — "
        f"{r.get('description', '')} — {money(r.get('amount'))}"
        for _, r in view_df.iterrows()
    ]

    selected = st.selectbox("Select request", labels)
    row = view_df.iloc[labels.index(selected)].to_dict()

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
    st.markdown("### Management Decision")

    decision = st.radio(
        "Decision",
        ["APPROVE", "DEFER", "DENY"],
        horizontal=True,
    )

    notes = st.text_area(
        "Manager notes",
        placeholder="Optional context, conditions, offsets, or follow-up instructions."
    )

    if st.button("Save Management Decision", type="primary"):
        save_decision(
            row=row,
            recommendation=recommendation,
            suggestion=suggestion,
            decision=decision,
            reviewer=reviewer,
            notes=notes,
        )
        st.success(
            f"{row.get('request_id', '')} saved as {decision}. Refresh the page to update request status."
        )


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
        "Historical EADA comparison data for Sonoma State and CSU Division II peers."
    )

    if peer_comparison_df.empty:
        st.warning("Peer comparison dataset is not loaded.")
    else:
        st.dataframe(peer_comparison_df, width="stretch", hide_index=True)

    if not team_benchmark_df.empty:
        with st.expander("Team Benchmark Data"):
            st.dataframe(team_benchmark_df, width="stretch", hide_index=True)

    if not cost_drivers_df.empty:
        with st.expander("Cost Drivers"):
            st.dataframe(cost_drivers_df, width="stretch", hide_index=True)

    if not team_summary_df.empty:
        with st.expander("Team Summary"):
            st.dataframe(team_summary_df, width="stretch", hide_index=True)


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
        "Audit trail of management approvals, deferrals, denials, and KORBI recommendations."
    )

    current_decisions = read_df(FILES["decisions"])

    if current_decisions.empty:
        st.info("No management decisions have been recorded yet.")
    else:
        st.dataframe(current_decisions, width="stretch", hide_index=True)

        if "manager_decision" in current_decisions.columns:
            counts = current_decisions["manager_decision"].value_counts().to_dict()

            d1, d2, d3 = st.columns(3)
            d1.metric("Approved", counts.get("APPROVE", 0))
            d2.metric("Deferred", counts.get("DEFER", 0))
            d3.metric("Denied", counts.get("DENY", 0))

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
