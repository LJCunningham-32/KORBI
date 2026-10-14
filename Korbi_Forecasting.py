import csv
from pathlib import Path


# --------------------------------------------------
# KORBI FORECASTING ENGINE
# Knowledge & Operations Resource
# for Business Intelligence
# --------------------------------------------------


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

BUDGET_FILE = (
    PROCESSED_FOLDER
    / "sonoma_proposed_athletics_budget.csv"
)

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
# LOAD PROGRAM BUDGETS
# --------------------------------------------------

def load_program_budgets(rows):

    programs = {}

    for row in rows:

        if row["expense_line"] != "TOTAL EXPENSES":
            continue

        programs[row["program_code"]] = {
            "program_name":
                row["program_name"],

            "program_budget":
                money(row["amount"]),
        }

    return programs


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
            "category_budget":
                money(row["category_budget"]),

            "budget_status":
                row["budget_status"],
        }

    return budgets


# --------------------------------------------------
# LOAD FORECAST ASSUMPTIONS
# --------------------------------------------------

def load_forecasts(rows):

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
# GET PROGRAM TRANSACTIONS
# --------------------------------------------------

def get_program_transactions(
    ledger,
    program_code
):

    return [
        row
        for row in ledger
        if row["program_code"] == program_code
    ]


# --------------------------------------------------
# CALCULATE ACTUALS
# --------------------------------------------------

def calculate_actual(
    transactions,
    category
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["expense_category"] == category
        and row["transaction_type"] == "ACTUAL"
        and row["status"] == "PAID"
    )


# --------------------------------------------------
# CALCULATE OPEN COMMITMENTS
# --------------------------------------------------

def calculate_commitments(
    transactions,
    category
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["expense_category"] == category
        and row["transaction_type"] == "PO"
        and row["status"] == "OPEN"
    )


# --------------------------------------------------
# CALCULATE PENDING REQUESTS
# --------------------------------------------------

def calculate_pending_requests(
    transactions,
    category
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["expense_category"] == category
        and row["transaction_type"]
        == "PURCHASE_REQUEST"
        and row["status"] == "PENDING"
    )


# --------------------------------------------------
# FORECAST RISK
# --------------------------------------------------

def classify_forecast(
    budget,
    projected_year_end
):

    if budget <= 0:
        return "NO BUDGET DATA"

    used_percent = (
        projected_year_end
        / budget
        * 100
    )

    remaining = (
        budget
        - projected_year_end
    )

    if remaining < 0:
        return "PROJECTED OVER BUDGET"

    elif used_percent >= 95:
        return "PROJECTED HIGH RISK"

    elif used_percent >= 85:
        return "PROJECTED CAUTION"

    else:
        return "PROJECTED WITHIN BUDGET"


# --------------------------------------------------
# BUILD FORECAST
# --------------------------------------------------

def build_forecast(
    program_code,
    category,
    programs,
    category_budgets,
    forecasts,
    ledger
):

    program = programs.get(
        program_code
    )

    if program is None:

        return None

    category_key = (
        program_code,
        category,
    )

    category_info = (
        category_budgets.get(
            category_key
        )
    )

    if category_info is None:

        return None

    forecast_info = (
        forecasts.get(
            category_key,
            {
                "expected_remaining_spend": 0,
                "forecast_status":
                    "NO FORECAST ASSUMPTION",
            }
        )
    )

    transactions = (
        get_program_transactions(
            ledger,
            program_code
        )
    )

    actual = calculate_actual(
        transactions,
        category
    )

    commitments = (
        calculate_commitments(
            transactions,
            category
        )
    )

    pending = (
        calculate_pending_requests(
            transactions,
            category
        )
    )

    expected_remaining = (
        forecast_info[
            "expected_remaining_spend"
        ]
    )

    current_obligated = (
        actual
        + commitments
        + pending
    )

    projected_year_end = (
        current_obligated
        + expected_remaining
    )

    category_budget = (
        category_info[
            "category_budget"
        ]
    )

    projected_remaining = (
        category_budget
        - projected_year_end
    )

    projected_used = (
        projected_year_end
        / category_budget
        * 100
        if category_budget > 0
        else 0
    )

    forecast_decision = (
        classify_forecast(
            category_budget,
            projected_year_end
        )
    )

    return {
        "program_code":
            program_code,

        "program_name":
            program["program_name"],

        "category":
            category,

        "category_budget":
            category_budget,

        "actual":
            actual,

        "commitments":
            commitments,

        "pending":
            pending,

        "current_obligated":
            current_obligated,

        "expected_remaining":
            expected_remaining,

        "projected_year_end":
            projected_year_end,

        "projected_remaining":
            projected_remaining,

        "projected_used":
            projected_used,

        "forecast_decision":
            forecast_decision,

        "forecast_status":
            forecast_info[
                "forecast_status"
            ],
    }


# --------------------------------------------------
# DISPLAY FORECAST
# --------------------------------------------------

def print_forecast(result):

    print()
    print(result["program_name"])
    print("-" * len(result["program_name"]))

    print(
        f"Category:                 "
        f"{result['category']}"
    )

    print(
        f"Category Budget:          "
        f"${result['category_budget']:,.0f}"
    )

    print()

    print(
        f"Actual Spend:             "
        f"${result['actual']:,.0f}"
    )

    print(
        f"Open Commitments:         "
        f"${result['commitments']:,.0f}"
    )

    print(
        f"Pending Requests:         "
        f"${result['pending']:,.0f}"
    )

    print(
        f"Current Obligated:        "
        f"${result['current_obligated']:,.0f}"
    )

    print(
        f"Expected Remaining Spend: "
        f"${result['expected_remaining']:,.0f}"
    )

    print()

    print(
        f"Projected Year-End Spend: "
        f"${result['projected_year_end']:,.0f}"
    )

    print(
        f"Projected Remaining:      "
        f"${result['projected_remaining']:,.0f}"
    )

    print(
        f"Projected Budget Used:    "
        f"{result['projected_used']:.1f}%"
    )

    print(
        f"KORBI Forecast:           "
        f"{result['forecast_decision']}"
    )

    print(
        f"Forecast Data Status:     "
        f"{result['forecast_status']}"
    )


# --------------------------------------------------
# DEPARTMENT FORECAST SUMMARY
# --------------------------------------------------

def print_department_summary(
    results
):

    total_budget = sum(
        row["category_budget"]
        for row in results
    )

    total_actual = sum(
        row["actual"]
        for row in results
    )

    total_commitments = sum(
        row["commitments"]
        for row in results
    )

    total_pending = sum(
        row["pending"]
        for row in results
    )

    total_expected = sum(
        row["expected_remaining"]
        for row in results
    )

    total_projected = sum(
        row["projected_year_end"]
        for row in results
    )

    total_remaining = (
        total_budget
        - total_projected
    )

    used_percent = (
        total_projected
        / total_budget
        * 100
        if total_budget > 0
        else 0
    )

    print()
    print("DEPARTMENT FORECAST SUMMARY")
    print("===========================")

    print(
        f"Category Budgets:         "
        f"${total_budget:,.0f}"
    )

    print(
        f"Actual Spend:             "
        f"${total_actual:,.0f}"
    )

    print(
        f"Open Commitments:         "
        f"${total_commitments:,.0f}"
    )

    print(
        f"Pending Requests:         "
        f"${total_pending:,.0f}"
    )

    print(
        f"Expected Remaining Spend: "
        f"${total_expected:,.0f}"
    )

    print(
        f"Projected Year-End Spend: "
        f"${total_projected:,.0f}"
    )

    print(
        f"Projected Remaining:      "
        f"${total_remaining:,.0f}"
    )

    print(
        f"Projected Budget Used:    "
        f"{used_percent:.1f}%"
    )

    print(
        f"Department Forecast:      "
        f"{classify_forecast(total_budget, total_projected)}"
    )


# --------------------------------------------------
# RUN KORBI FORECASTING
# --------------------------------------------------

def run_korbi_forecast():

    program_rows = read_csv(
        BUDGET_FILE
    )

    category_rows = read_csv(
        CATEGORY_BUDGET_FILE
    )

    ledger = read_csv(
        LEDGER_FILE
    )

    forecast_rows = read_csv(
        FORECAST_FILE
    )

    programs = load_program_budgets(
        program_rows
    )

    category_budgets = (
        load_category_budgets(
            category_rows
        )
    )

    forecasts = load_forecasts(
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

    print("YEAR-END FORECASTING ENGINE")
    print("===========================")

    print()

    print(
        "TEST MODE - Expected remaining "
        "spend uses simulated assumptions."
    )

    print(
        "Category budgets marked VERIFIED "
        "come from the Sonoma proposed model."
    )

    results = []

    for key in category_budgets:

        program_code = key[0]
        category = key[1]

        result = build_forecast(
            program_code,
            category,
            programs,
            category_budgets,
            forecasts,
            ledger
        )

        if result is None:
            continue

        results.append(
            result
        )

        print_forecast(
            result
        )

    print_department_summary(
        results
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    try:

        run_korbi_forecast()

    except Exception as error:

        print()
        print("KORBI FORECAST ERROR")
        print("====================")
        print(error)