import csv
from pathlib import Path


# ============================================================
# KORBI
# Knowledge & Operations Resource for Business Intelligence
#
# MASS PURCHASE REQUEST TRIAGE
#
# Adds:
# - Financial recommendation
# - Before/after budget position
# - Request % of annual sport budget
# - Remaining cushion before/after
# - Deficit created
# - Plain-language budget impact summary
#
# TEST / SIMULATION ENVIRONMENT
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent

RAW_FOLDER = PROJECT_FOLDER / "Data" / "Raw"
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"


INPUT_FILE = (
    RAW_FOLDER
    / "korbi_q2_purchase_requests_semantic.csv"
)

BUDGET_FILE = (
    PROCESSED_FOLDER
    / "korbi_category_budgets.csv"
)

LEDGER_FILE = (
    PROCESSED_FOLDER
    / "korbi_operational_ledger.csv"
)

FUTURE_FILE = (
    PROCESSED_FOLDER
    / "korbi_future_expenses.csv"
)

REQUEST_FILE = (
    PROCESSED_FOLDER
    / "korbi_purchase_requests.csv"
)

DEPARTMENT_FILE = (
    PROCESSED_FOLDER
    / "korbi_department_q1_snapshot.csv"
)

OUTPUT_FILE = (
    PROCESSED_FOLDER
    / "korbi_bulk_triage_results.csv"
)


SPORT_SEASONS = {
    "MBB": "WINTER",
    "WBB": "WINTER",
    "MGO": "FALL_SPRING",
    "WGO": "FALL_SPRING",
    "MSO": "FALL",
    "WSO": "FALL",
    "MCC": "FALL",
    "WCC": "FALL",
    "WVB": "FALL",
    "WSB": "SPRING",
}


OUTPUT_FIELDS = [
    "request_id",
    "program_code",
    "program_name",
    "category_code",
    "category_name",
    "requester",
    "vendor",
    "description",
    "business_justification",
    "priority",
    "amount",

    "season",
    "annual_budget",
    "q1_actuals",
    "open_pos",
    "scheduled_future",
    "expected_future",
    "existing_pending_requests",

    "baseline_projected",
    "baseline_remaining",
    "baseline_percent",

    "projected_with_request",
    "remaining_with_request",
    "percent_with_request",

    "request_percent_of_budget",
    "cushion_reduction_percent",
    "deficit_created",

    "financial_status",
    "department_forecast_percent",
    "department_uncommitted_reserve",

    "korbi_recommendation",
    "korbi_reason",
    "suggested_action",
    "budget_impact_summary",
]


# ============================================================
# HELPERS
# ============================================================

def read_csv(file_path):

    if not file_path.exists():
        return []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


def write_csv(file_path, rows, fieldnames):

    with open(
        file_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


def safe_float(value):

    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


def money(value):

    value = safe_float(value)

    if value < 0:
        return f"-${abs(value):,.0f}"

    return f"${value:,.0f}"


def percent(value):

    return f"{safe_float(value):.1f}%"


# ============================================================
# LOAD BUDGETS
# ============================================================

def load_budgets():

    rows = read_csv(BUDGET_FILE)

    if not rows:
        raise FileNotFoundError(
            f"No budget data found:\n{BUDGET_FILE}"
        )

    budgets = {}

    for row in rows:

        budgets[row["program_code"]] = {
            "program_name":
                row["program_name"],

            "budget":
                safe_float(
                    row["category_budget"]
                ),
        }

    return budgets


# ============================================================
# SPORT FINANCIAL POSITION
# ============================================================

def calculate_sport_position(
    program_code,
    annual_budget
):

    ledger = read_csv(LEDGER_FILE)
    future = read_csv(FUTURE_FILE)
    requests = read_csv(REQUEST_FILE)

    q1_actuals = sum(
        safe_float(row["amount"])
        for row in ledger
        if (
            row.get("program_code") == program_code
            and row.get("transaction_type") == "ACTUAL"
            and row.get("status") == "PAID"
        )
    )

    open_pos = sum(
        safe_float(row["amount"])
        for row in ledger
        if (
            row.get("program_code") == program_code
            and row.get("transaction_type") == "PO"
            and row.get("status") == "OPEN"
        )
    )

    scheduled_future = sum(
        safe_float(row["amount"])
        for row in future
        if (
            row.get("program_code") == program_code
            and row.get("status") == "PLANNED"
            and row.get("confidence") == "HIGH"
        )
    )

    expected_future = sum(
        safe_float(row["amount"])
        for row in future
        if (
            row.get("program_code") == program_code
            and row.get("status") == "PLANNED"
            and row.get("confidence") in {
                "MEDIUM",
                "LOW",
            }
        )
    )

    existing_pending = sum(
        safe_float(row["amount"])
        for row in requests
        if (
            row.get("program_code") == program_code
            and row.get("status") == "PENDING"
        )
    )

    baseline_projected = (
        q1_actuals
        + open_pos
        + scheduled_future
        + expected_future
        + existing_pending
    )

    baseline_remaining = (
        annual_budget
        - baseline_projected
    )

    baseline_percent = (
        baseline_projected
        / annual_budget
        * 100
        if annual_budget
        else 0
    )

    return {
        "q1_actuals": q1_actuals,
        "open_pos": open_pos,
        "scheduled_future": scheduled_future,
        "expected_future": expected_future,
        "existing_pending": existing_pending,
        "baseline_projected": baseline_projected,
        "baseline_remaining": baseline_remaining,
        "baseline_percent": baseline_percent,
    }


# ============================================================
# DEPARTMENT POSITION
# ============================================================

def get_department_position():

    rows = read_csv(DEPARTMENT_FILE)

    if not rows:
        return {
            "annual_budget": 0,
            "projected": 0,
            "reserve": 0,
            "forecast_percent": 0,
        }

    annual = sum(
        safe_float(row["annual_budget"])
        for row in rows
    )

    projected = sum(
        safe_float(row["projected_year_end"])
        for row in rows
    )

    reserve = sum(
        safe_float(row["uncommitted_reserve"])
        for row in rows
    )

    forecast_percent = (
        projected
        / annual
        * 100
        if annual
        else 0
    )

    return {
        "annual_budget": annual,
        "projected": projected,
        "reserve": reserve,
        "forecast_percent": forecast_percent,
    }


# ============================================================
# FINANCIAL STATUS
# ============================================================

def classify_financial_status(
    projected_percent
):

    projected_percent = round(
        projected_percent,
        1
    )

    if projected_percent > 100:
        return "OVER BUDGET"

    if projected_percent >= 95:
        return "HIGH RISK"

    if projected_percent >= 90:
        return "CAUTION"

    if projected_percent >= 80:
        return "MONITOR"

    return "HEALTHY"


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def build_recommendation(
    priority,
    category_code,
    projected_percent,
    department_forecast
):

    projected_percent = round(
        projected_percent,
        1
    )

    if projected_percent > 100:

        if priority == "CRITICAL":

            return (
                "ESCALATE - CRITICAL NEED",
                (
                    "The request would push the program "
                    "over its projected annual budget, "
                    "but the need is classified as critical."
                ),
                (
                    "Identify a funding transfer, offset, "
                    "emergency source, or senior approval."
                ),
            )

        return (
            "DENY / DEFER",
            (
                "The request would push projected "
                "year-end spending above the program budget."
            ),
            (
                "Defer or identify documented savings "
                "before reconsideration."
            ),
        )

    if projected_percent >= 95:

        if priority == "CRITICAL":

            return (
                "ESCALATE FOR APPROVAL",
                (
                    "The request is critical but would "
                    "leave almost no remaining flexibility."
                ),
                (
                    "Require management review before "
                    "committing funds."
                ),
            )

        if priority == "NECESSARY":

            return (
                "HOLD FOR REVIEW",
                (
                    "The request appears necessary, but "
                    "the program would remain in the "
                    "high-risk range."
                ),
                (
                    "Confirm remaining seasonal costs "
                    "and identify an offset if possible."
                ),
            )

        return (
            "DEFER",
            (
                "The request is an enhancement and the "
                "program is already near its annual limit."
            ),
            (
                "Preserve the remaining cushion for "
                "essential obligations."
            ),
        )

    if projected_percent >= 90:

        if priority == "CRITICAL":

            return (
                "APPROVE WITH MANAGEMENT REVIEW",
                (
                    "The request remains within budget "
                    "and addresses a critical need, but "
                    "the program would enter the caution range."
                ),
                (
                    "Confirm no higher-priority obligation "
                    "is at risk."
                ),
            )

        if priority == "NECESSARY":

            return (
                "HOLD FOR REVIEW",
                (
                    "The request is useful, but projected "
                    "spending would leave limited flexibility."
                ),
                (
                    "Review remaining season obligations "
                    "before issuing the purchase."
                ),
            )

        return (
            "DEFER",
            (
                "The request is an enhancement and would "
                "leave the program with limited cushion."
            ),
            (
                "Revisit later if savings develop."
            ),
        )

    if projected_percent >= 80:

        if priority == "CRITICAL":

            return (
                "APPROVE",
                (
                    "The request addresses a critical need "
                    "and forecasted budget capacity remains."
                ),
                (
                    "Proceed through normal purchasing controls."
                ),
            )

        if priority == "NECESSARY":

            return (
                "APPROVE WITH CAUTION",
                (
                    "The request appears necessary and "
                    "fits within the forecast."
                ),
                (
                    "Proceed while monitoring future obligations."
                ),
            )

        return (
            "CONSIDER IF FUNDS REMAIN",
            (
                "The request is discretionary and the "
                "program is already using a meaningful "
                "share of its projected budget."
            ),
            (
                "Compare the benefit against preserving "
                "year-end flexibility."
            ),
        )

    if priority == "CRITICAL":

        return (
            "APPROVE",
            (
                "The request addresses a critical need "
                "and adequate forecasted capacity exists."
            ),
            (
                "Proceed through normal purchasing controls."
            ),
        )

    if priority == "NECESSARY":

        return (
            "APPROVE",
            (
                "The request appears necessary and the "
                "program retains a healthy financial cushion."
            ),
            (
                "Proceed if normal documentation and "
                "procurement requirements are satisfied."
            ),
        )

    recommendation = "CONSIDER"

    reason = (
        "The enhancement fits within the current forecast."
    )

    action = (
        "Evaluate strategic value before approval."
    )

    if department_forecast >= 96:

        recommendation = (
            "CONSIDER WITH CAUTION"
        )

        reason += (
            " Department-wide spending is also forecast "
            "near the annual plan."
        )

        action = (
            "Confirm the benefit justifies using limited "
            "department financial flexibility."
        )

    if (
        category_code == "TECH"
        and priority == "ENHANCEMENT"
    ):

        reason += (
            " Review any recurring subscription or "
            "renewal costs before approval."
        )

    if category_code == "TRAV":

        reason += (
            " Confirm the travel is tied to the approved "
            "competition schedule."
        )

    return (
        recommendation,
        reason,
        action,
    )


# ============================================================
# BUDGET IMPACT SUMMARY
# ============================================================

def build_budget_impact_summary(
    annual_budget,
    amount,
    baseline_remaining,
    baseline_percent,
    remaining_with_request,
    percent_with_request
):

    request_percent = (
        amount
        / annual_budget
        * 100
        if annual_budget
        else 0
    )

    if baseline_remaining > 0:

        cushion_reduction_percent = (
            amount
            / baseline_remaining
            * 100
        )

    else:

        cushion_reduction_percent = 100.0

    deficit_created = max(
        0,
        -remaining_with_request
    )

    if deficit_created > 0:

        impact_sentence = (
            f"This request represents "
            f"{request_percent:.1f}% of the annual "
            f"operating budget and would move the "
            f"program from {baseline_percent:.1f}% "
            f"to {percent_with_request:.1f}% utilized. "
            f"It would eliminate the remaining budget "
            f"cushion and create a projected deficit of "
            f"{money(deficit_created)}."
        )

    elif remaining_with_request <= 5000:

        impact_sentence = (
            f"This request represents "
            f"{request_percent:.1f}% of the annual "
            f"operating budget and would move the "
            f"program from {baseline_percent:.1f}% "
            f"to {percent_with_request:.1f}% utilized. "
            f"Only {money(remaining_with_request)} "
            f"would remain after the purchase."
        )

    else:

        impact_sentence = (
            f"This request represents "
            f"{request_percent:.1f}% of the annual "
            f"operating budget and would move the "
            f"program from {baseline_percent:.1f}% "
            f"to {percent_with_request:.1f}% utilized. "
            f"The remaining projected cushion would be "
            f"{money(remaining_with_request)}, compared "
            f"with {money(baseline_remaining)} before "
            f"the request."
        )

    return (
        request_percent,
        cushion_reduction_percent,
        deficit_created,
        impact_sentence
    )


# ============================================================
# TRIAGE REQUESTS
# ============================================================

def triage_requests():

    incoming = read_csv(INPUT_FILE)

    if not incoming:

        raise FileNotFoundError(
            f"No requests found:\n{INPUT_FILE}"
        )

    budgets = load_budgets()

    department = get_department_position()

    results = []

    batch_exposure = {}

    for request in incoming:

        code = request["program_code"]

        if code not in budgets:

            print(
                f"SKIPPED: {request['request_id']} "
                f"- no budget found for {code}"
            )

            continue

        budget = budgets[code]["budget"]

        position = calculate_sport_position(
            code,
            budget
        )

        prior_batch_requests = (
            batch_exposure.get(
                code,
                0
            )
        )

        baseline_projected = (
            position[
                "baseline_projected"
            ]
            + prior_batch_requests
        )

        baseline_remaining = (
            budget
            - baseline_projected
        )

        baseline_percent = (
            baseline_projected
            / budget
            * 100
            if budget
            else 0
        )

        amount = safe_float(
            request["amount"]
        )

        projected_with_request = (
            baseline_projected
            + amount
        )

        remaining_with_request = (
            budget
            - projected_with_request
        )

        percent_with_request = (
            projected_with_request
            / budget
            * 100
            if budget
            else 0
        )

        financial_status = (
            classify_financial_status(
                percent_with_request
            )
        )

        (
            recommendation,
            reason,
            suggested_action
        ) = build_recommendation(
            request["priority"],
            request["category_code"],
            percent_with_request,
            department[
                "forecast_percent"
            ],
        )

        (
            request_percent,
            cushion_reduction_percent,
            deficit_created,
            budget_impact_summary
        ) = build_budget_impact_summary(
            budget,
            amount,
            baseline_remaining,
            baseline_percent,
            remaining_with_request,
            percent_with_request
        )

        result = {
            "request_id":
                request["request_id"],

            "program_code":
                code,

            "program_name":
                request["program_name"],

            "category_code":
                request["category_code"],

            "category_name":
                request["category_name"],

            "requester":
                request["requester"],

            "vendor":
                request["vendor"],

            "description":
                request["description"],

            "business_justification":
                request["business_justification"],

            "priority":
                request["priority"],

            "amount":
                amount,

            "season":
                SPORT_SEASONS.get(
                    code,
                    "UNKNOWN"
                ),

            "annual_budget":
                budget,

            "q1_actuals":
                position["q1_actuals"],

            "open_pos":
                position["open_pos"],

            "scheduled_future":
                position["scheduled_future"],

            "expected_future":
                position["expected_future"],

            "existing_pending_requests":
                (
                    position["existing_pending"]
                    + prior_batch_requests
                ),

            "baseline_projected":
                baseline_projected,

            "baseline_remaining":
                baseline_remaining,

            "baseline_percent":
                baseline_percent,

            "projected_with_request":
                projected_with_request,

            "remaining_with_request":
                remaining_with_request,

            "percent_with_request":
                percent_with_request,

            "request_percent_of_budget":
                request_percent,

            "cushion_reduction_percent":
                cushion_reduction_percent,

            "deficit_created":
                deficit_created,

            "financial_status":
                financial_status,

            "department_forecast_percent":
                department[
                    "forecast_percent"
                ],

            "department_uncommitted_reserve":
                department["reserve"],

            "korbi_recommendation":
                recommendation,

            "korbi_reason":
                reason,

            "suggested_action":
                suggested_action,

            "budget_impact_summary":
                budget_impact_summary,
        }

        results.append(result)

        batch_exposure[code] = (
            prior_batch_requests
            + amount
        )

    return results


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    print()
    print("KORBI Q2 PURCHASE REQUEST TRIAGE")
    print("===============================")

    total_requested = sum(
        row["amount"]
        for row in results
    )

    print()
    print(
        f"Requests Reviewed: "
        f"{len(results)}"
    )

    print(
        f"Total Requested:   "
        f"{money(total_requested)}"
    )

    print()
    print("TRIAGE LIST")
    print("===========")

    for row in results:

        print()

        print(
            f"{row['request_id']} | "
            f"{row['program_name']}"
        )

        print(
            f"  Category:       "
            f"{row['category_code']} - "
            f"{row['category_name']}"
        )

        print(
            f"  Request:        "
            f"{row['description']}"
        )

        print(
            f"  Priority:       "
            f"{row['priority']}"
        )

        print(
            f"  Amount:         "
            f"{money(row['amount'])}"
        )

        print(
            f"  Before Request: "
            f"{percent(row['baseline_percent'])}"
        )

        print(
            f"  After Request:  "
            f"{percent(row['percent_with_request'])}"
        )

        print(
            f"  Remaining:      "
            f"{money(row['remaining_with_request'])}"
        )

        print(
            f"  Status:         "
            f"{row['financial_status']}"
        )

        print(
            f"  KORBI:          "
            f"{row['korbi_recommendation']}"
        )

        print()
        print("  Budget Impact:")

        print(
            f"  {row['budget_impact_summary']}"
        )

    print()
    print("RECOMMENDATION SUMMARY")
    print("======================")

    counts = {}

    for row in results:

        recommendation = (
            row["korbi_recommendation"]
        )

        counts[recommendation] = (
            counts.get(
                recommendation,
                0
            )
            + 1
        )

    for recommendation in sorted(
        counts.keys()
    ):

        print(
            f"{recommendation}: "
            f"{counts[recommendation]}"
        )


# ============================================================
# MAIN
# ============================================================

def run():

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()
    print(
        "MASS PURCHASE REQUEST TRIAGE"
    )

    results = triage_requests()

    write_csv(
        OUTPUT_FILE,
        results,
        OUTPUT_FIELDS
    )

    display_results(
        results
    )

    print()
    print("TRIAGE FILE SAVED")
    print("=================")

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "This run evaluates requests only. "
        "No requests are approved and no POs "
        "are created automatically."
    )


if __name__ == "__main__":

    try:

        run()

    except Exception as error:

        print()
        print("KORBI BULK TRIAGE ERROR")
        print("=======================")
        print(error)