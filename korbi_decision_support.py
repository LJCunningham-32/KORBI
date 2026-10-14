import csv
from pathlib import Path


# --------------------------------------------------
# KORBI DECISION SUPPORT ENGINE
# Knowledge & Operations Resource
# for Business Intelligence
# --------------------------------------------------


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

CATEGORY_BUDGET_FILE = (
    PROCESSED_FOLDER
    / "korbi_category_budgets.csv"
)

LEDGER_FILE = (
    PROCESSED_FOLDER
    / "korbi_operational_ledger.csv"
)

FORECAST_FILE = (
    PROCESSED_FOLDER
    / "korbi_forecast_assumptions.csv"
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def read_csv(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


def money(value):

    if value in ["", None]:
        return 0

    return int(float(value))


# --------------------------------------------------
# LOAD CATEGORY BUDGETS
# --------------------------------------------------

def load_category_budgets(rows):

    budgets = {}

    for row in rows:

        key = (
            row["program_code"],
            row["expense_category"],
        )

        budgets[key] = {
            "program_name":
                row["program_name"],

            "category_budget":
                money(row["category_budget"]),

            "budget_status":
                row["budget_status"],

            "source":
                row["source"],
        }

    return budgets


# --------------------------------------------------
# LOAD FORECAST ASSUMPTIONS
# --------------------------------------------------

def load_forecast_assumptions(rows):

    forecasts = {}

    for row in rows:

        key = (
            row["program_code"],
            row["expense_category"],
        )

        forecasts[key] = {
            "expected_remaining_spend":
                money(
                    row[
                        "expected_remaining_spend"
                    ]
                ),

            "forecast_status":
                row["forecast_status"],
        }

    return forecasts


# --------------------------------------------------
# LEDGER CALCULATIONS
# --------------------------------------------------

def get_transactions(
    ledger,
    program_code,
    category
):

    return [
        row
        for row in ledger
        if row["program_code"] == program_code
        and row["expense_category"] == category
    ]


def calculate_actual(
    transactions
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["transaction_type"] == "ACTUAL"
        and row["status"] == "PAID"
    )


def calculate_commitments(
    transactions
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["transaction_type"] == "PO"
        and row["status"] == "OPEN"
    )


def get_pending_requests(
    transactions
):

    return [
        row
        for row in transactions
        if row["transaction_type"]
        == "PURCHASE_REQUEST"
        and row["status"] == "PENDING"
    ]


# --------------------------------------------------
# FORECAST CLASSIFICATION
# --------------------------------------------------

def classify_position(
    budget,
    projected_spend
):

    if budget <= 0:
        return "NO BUDGET DATA"

    remaining = (
        budget
        - projected_spend
    )

    used_percent = (
        projected_spend
        / budget
        * 100
    )

    if remaining < 0:
        return "OVER BUDGET"

    elif used_percent >= 95:
        return "HIGH RISK"

    elif used_percent >= 85:
        return "CAUTION"

    else:
        return "WITHIN BUDGET"


# --------------------------------------------------
# BUILD RECOMMENDATION
# --------------------------------------------------

def determine_recommendation(
    approve_status,
    deny_status
):

    # Approving still leaves the category healthy.
    if approve_status == "WITHIN BUDGET":

        return (
            "APPROVE",
            "The request can be approved and the "
            "category is still projected to finish "
            "within budget."
        )

    # Approving creates pressure, but does not exceed
    # the budget. Management should assess necessity.
    if approve_status in [
        "CAUTION",
        "HIGH RISK",
    ]:

        return (
            "HOLD FOR REVIEW",
            "The request remains technically within "
            "budget, but approval creates elevated "
            "year-end budget risk. Management should "
            "confirm the purchase is necessary and "
            "that remaining obligations are realistic."
        )

    # Approval creates a deficit, but denying or
    # deferring the request avoids the deficit.
    if (
        approve_status == "OVER BUDGET"
        and deny_status != "OVER BUDGET"
    ):

        return (
            "DENY / DEFER",
            "Approving the request is projected to "
            "exceed the category budget. Denying or "
            "deferring the request removes the "
            "projected deficit."
        )

    # The category is already projected over budget
    # even without the pending request.
    if (
        approve_status == "OVER BUDGET"
        and deny_status == "OVER BUDGET"
    ):

        return (
            "ESCALATE FOR BUDGET ACTION",
            "The category is projected to exceed "
            "budget even if this request is denied "
            "or deferred. Additional savings, a "
            "budget transfer, or management action "
            "is required."
        )

    return (
        "MANUAL REVIEW",
        "KORBI does not have enough verified "
        "information to make a clear recommendation."
    )


# --------------------------------------------------
# BUILD SCENARIO
# --------------------------------------------------

def evaluate_request_scenario(
    program_code,
    category,
    request,
    budget_info,
    forecast_info,
    ledger
):

    transactions = get_transactions(
        ledger,
        program_code,
        category
    )

    actual = calculate_actual(
        transactions
    )

    commitments = calculate_commitments(
        transactions
    )

    expected_remaining = (
        forecast_info[
            "expected_remaining_spend"
        ]
    )

    request_amount = money(
        request["amount"]
    )

    budget = (
        budget_info[
            "category_budget"
        ]
    )

    # ----------------------------------------------
    # APPROVE SCENARIO
    # ----------------------------------------------

    approve_projected = (
        actual
        + commitments
        + request_amount
        + expected_remaining
    )

    approve_remaining = (
        budget
        - approve_projected
    )

    approve_used = (
        approve_projected
        / budget
        * 100
        if budget > 0
        else 0
    )

    approve_status = classify_position(
        budget,
        approve_projected
    )

    # ----------------------------------------------
    # DENY / DEFER SCENARIO
    # ----------------------------------------------

    deny_projected = (
        actual
        + commitments
        + expected_remaining
    )

    deny_remaining = (
        budget
        - deny_projected
    )

    deny_used = (
        deny_projected
        / budget
        * 100
        if budget > 0
        else 0
    )

    deny_status = classify_position(
        budget,
        deny_projected
    )

    # ----------------------------------------------
    # REQUIRED SAVINGS
    # ----------------------------------------------

    required_savings_if_approved = max(
        0,
        approve_projected
        - budget
    )

    required_savings_if_denied = max(
        0,
        deny_projected
        - budget
    )

    # ----------------------------------------------
    # RECOMMENDATION
    # ----------------------------------------------

    recommendation, reason = (
        determine_recommendation(
            approve_status,
            deny_status
        )
    )

    return {
        "program_name":
            budget_info["program_name"],

        "program_code":
            program_code,

        "category":
            category,

        "request_id":
            request["transaction_id"],

        "vendor":
            request["vendor"],

        "description":
            request["description"],

        "request_amount":
            request_amount,

        "budget":
            budget,

        "budget_status":
            budget_info["budget_status"],

        "budget_source":
            budget_info["source"],

        "forecast_status":
            forecast_info["forecast_status"],

        "actual":
            actual,

        "commitments":
            commitments,

        "expected_remaining":
            expected_remaining,

        "approve_projected":
            approve_projected,

        "approve_remaining":
            approve_remaining,

        "approve_used":
            approve_used,

        "approve_status":
            approve_status,

        "deny_projected":
            deny_projected,

        "deny_remaining":
            deny_remaining,

        "deny_used":
            deny_used,

        "deny_status":
            deny_status,

        "required_savings_if_approved":
            required_savings_if_approved,

        "required_savings_if_denied":
            required_savings_if_denied,

        "recommendation":
            recommendation,

        "reason":
            reason,
    }


# --------------------------------------------------
# DISPLAY REQUEST
# --------------------------------------------------

def print_decision(result):

    print()
    print(result["program_name"])
    print("-" * len(result["program_name"]))

    print(
        f"Request ID:               "
        f"{result['request_id']}"
    )

    print(
        f"Vendor:                   "
        f"{result['vendor']}"
    )

    print(
        f"Description:              "
        f"{result['description']}"
    )

    print(
        f"Category:                 "
        f"{result['category']}"
    )

    print(
        f"Request Amount:           "
        f"${result['request_amount']:,.0f}"
    )

    print()

    print("CURRENT PLANNING POSITION")
    print("-------------------------")

    print(
        f"Category Budget:          "
        f"${result['budget']:,.0f}"
    )

    print(
        f"Budget Data Status:       "
        f"{result['budget_status']}"
    )

    print(
        f"Forecast Data Status:     "
        f"{result['forecast_status']}"
    )

    print(
        f"Actual Spend:             "
        f"${result['actual']:,.0f}"
    )

    print(
        f"Open Commitments:         "
        f"${result['commitments']:,.0f}"
    )

    print(
        f"Expected Remaining Spend: "
        f"${result['expected_remaining']:,.0f}"
    )

    print()

    print("SCENARIO A - APPROVE REQUEST")
    print("----------------------------")

    print(
        f"Projected Year-End Spend: "
        f"${result['approve_projected']:,.0f}"
    )

    print(
        f"Projected Remaining:      "
        f"${result['approve_remaining']:,.0f}"
    )

    print(
        f"Projected Budget Used:    "
        f"{result['approve_used']:.1f}%"
    )

    print(
        f"Budget Status:            "
        f"{result['approve_status']}"
    )

    print(
        f"Required Savings:         "
        f"${result['required_savings_if_approved']:,.0f}"
    )

    print()

    print("SCENARIO B - DENY / DEFER")
    print("-------------------------")

    print(
        f"Projected Year-End Spend: "
        f"${result['deny_projected']:,.0f}"
    )

    print(
        f"Projected Remaining:      "
        f"${result['deny_remaining']:,.0f}"
    )

    print(
        f"Projected Budget Used:    "
        f"{result['deny_used']:.1f}%"
    )

    print(
        f"Budget Status:            "
        f"{result['deny_status']}"
    )

    print(
        f"Required Savings:         "
        f"${result['required_savings_if_denied']:,.0f}"
    )

    print()

    print("KORBI RECOMMENDATION")
    print("--------------------")

    print(
        result[
            "recommendation"
        ]
    )

    print()

    print(
        f"Reason: {result['reason']}"
    )


# --------------------------------------------------
# MANAGEMENT SUMMARY
# --------------------------------------------------

def print_management_summary(
    results
):

    counts = {
        "APPROVE": 0,
        "HOLD FOR REVIEW": 0,
        "DENY / DEFER": 0,
        "ESCALATE FOR BUDGET ACTION": 0,
        "MANUAL REVIEW": 0,
    }

    for result in results:

        recommendation = (
            result[
                "recommendation"
            ]
        )

        if recommendation in counts:
            counts[
                recommendation
            ] += 1

    total_requested = sum(
        result["request_amount"]
        for result in results
    )

    total_deficit_if_approved = sum(
        result[
            "required_savings_if_approved"
        ]
        for result in results
    )

    total_deficit_without_requests = sum(
        result[
            "required_savings_if_denied"
        ]
        for result in results
    )

    print()
    print("MANAGEMENT DECISION SUMMARY")
    print("===========================")

    print(
        f"Requests Reviewed:        "
        f"{len(results)}"
    )

    print(
        f"Total Requested:          "
        f"${total_requested:,.0f}"
    )

    print()

    print(
        f"Approve:                  "
        f"{counts['APPROVE']}"
    )

    print(
        f"Hold for Review:          "
        f"{counts['HOLD FOR REVIEW']}"
    )

    print(
        f"Deny / Defer:             "
        f"{counts['DENY / DEFER']}"
    )

    print(
        f"Escalate:                 "
        f"{counts['ESCALATE FOR BUDGET ACTION']}"
    )

    print(
        f"Manual Review:            "
        f"{counts['MANUAL REVIEW']}"
    )

    print()

    print(
        f"Deficit if All Approved:  "
        f"${total_deficit_if_approved:,.0f}"
    )

    print(
        f"Deficit Without Requests: "
        f"${total_deficit_without_requests:,.0f}"
    )


# --------------------------------------------------
# RUN ENGINE
# --------------------------------------------------

def run_decision_support():

    budget_rows = read_csv(
        CATEGORY_BUDGET_FILE
    )

    ledger = read_csv(
        LEDGER_FILE
    )

    forecast_rows = read_csv(
        FORECAST_FILE
    )

    budgets = load_category_budgets(
        budget_rows
    )

    forecasts = load_forecast_assumptions(
        forecast_rows
    )

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()

    print("DECISION SUPPORT ENGINE")
    print("=======================")

    print()

    print(
        "TEST MODE - Transaction and forecast "
        "values are simulated."
    )

    print(
        "KORBI recommendations are management "
        "decision support only."
    )

    results = []

    for key, budget_info in budgets.items():

        program_code = key[0]
        category = key[1]

        transactions = get_transactions(
            ledger,
            program_code,
            category
        )

        requests = get_pending_requests(
            transactions
        )

        forecast_info = forecasts.get(
            key,
            {
                "expected_remaining_spend": 0,
                "forecast_status":
                    "NO FORECAST DATA",
            }
        )

        for request in requests:

            result = evaluate_request_scenario(
                program_code,
                category,
                request,
                budget_info,
                forecast_info,
                ledger
            )

            results.append(
                result
            )

            print_decision(
                result
            )

    print_management_summary(
        results
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    try:

        run_decision_support()

    except Exception as error:

        print()
        print("KORBI DECISION SUPPORT ERROR")
        print("============================")
        print(error)