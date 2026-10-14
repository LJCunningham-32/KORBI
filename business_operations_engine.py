import csv
from pathlib import Path


# --------------------------------------------------
# KORBI
# Knowledge & Operations Resource
# for Business Intelligence
# --------------------------------------------------


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

BUDGET_FILE = (
    PROCESSED_FOLDER
    / "sonoma_proposed_athletics_budget.csv"
)

LEDGER_FILE = (
    PROCESSED_FOLDER
    / "korbi_operational_ledger.csv"
)

CATEGORY_BUDGET_FILE = (
    PROCESSED_FOLDER
    / "korbi_category_budgets.csv"
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

def get_program_budgets(budget_data):

    programs = {}

    for row in budget_data:

        if row["expense_line"] != "TOTAL EXPENSES":
            continue

        code = row["program_code"]

        programs[code] = {
            "program_code": code,
            "program_name": row["program_name"],
            "approved_budget": money(row["amount"]),
        }

    return programs


# --------------------------------------------------
# LOAD CATEGORY BUDGETS
# --------------------------------------------------

def get_category_budgets(category_data):

    budgets = {}

    for row in category_data:

        key = (
            row["program_code"],
            row["expense_category"],
        )

        budgets[key] = {
            "category_budget":
                money(row["category_budget"]),

            "budget_status":
                row["budget_status"],

            "source":
                row["source"],
        }

    return budgets


# --------------------------------------------------
# GROUP LEDGER
# --------------------------------------------------

def group_transactions(ledger_data):

    grouped = {}

    for row in ledger_data:

        code = row["program_code"]

        if code not in grouped:
            grouped[code] = []

        grouped[code].append(row)

    return grouped


# --------------------------------------------------
# TRANSACTION CALCULATIONS
# --------------------------------------------------

def calculate_actual(
    transactions,
    category=None
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["transaction_type"] == "ACTUAL"
        and row["status"] == "PAID"
        and (
            category is None
            or row["expense_category"] == category
        )
    )


def calculate_commitments(
    transactions,
    category=None
):

    return sum(
        money(row["amount"])
        for row in transactions
        if row["transaction_type"] == "PO"
        and row["status"] == "OPEN"
        and (
            category is None
            or row["expense_category"] == category
        )
    )


def get_pending_requests(transactions):

    return [
        row
        for row in transactions
        if row["transaction_type"]
        == "PURCHASE_REQUEST"
        and row["status"] == "PENDING"
    ]


# --------------------------------------------------
# RISK CLASSIFICATION
# --------------------------------------------------

def classify_budget(
    budget,
    projected_spend
):

    if budget <= 0:
        return "NO BUDGET DATA"

    used_percent = (
        projected_spend
        / budget
        * 100
    )

    remaining = (
        budget
        - projected_spend
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
# EVALUATE PURCHASE REQUEST
# --------------------------------------------------

def evaluate_request(
    program,
    transactions,
    request,
    category_budgets
):

    request_amount = money(
        request["amount"]
    )

    expense_category = (
        request["expense_category"]
    )

    # ----------------------------------------------
    # PROGRAM LEVEL
    # ----------------------------------------------

    program_budget = (
        program["approved_budget"]
    )

    program_actual = (
        calculate_actual(
            transactions
        )
    )

    program_commitments = (
        calculate_commitments(
            transactions
        )
    )

    program_projected = (
        program_actual
        + program_commitments
        + request_amount
    )

    program_remaining = (
        program_budget
        - program_projected
    )

    program_used = (
        program_projected
        / program_budget
        * 100
        if program_budget > 0
        else 0
    )

    program_decision = (
        classify_budget(
            program_budget,
            program_projected
        )
    )

    # ----------------------------------------------
    # CATEGORY LEVEL
    # ----------------------------------------------

    category_key = (
        program["program_code"],
        expense_category,
    )

    category_info = (
        category_budgets.get(
            category_key
        )
    )

    if category_info:

        category_budget = (
            category_info[
                "category_budget"
            ]
        )

        category_actual = (
            calculate_actual(
                transactions,
                expense_category
            )
        )

        category_commitments = (
            calculate_commitments(
                transactions,
                expense_category
            )
        )

        category_projected = (
            category_actual
            + category_commitments
            + request_amount
        )

        category_remaining = (
            category_budget
            - category_projected
        )

        category_used = (
            category_projected
            / category_budget
            * 100
            if category_budget > 0
            else 0
        )

        category_decision = (
            classify_budget(
                category_budget,
                category_projected
            )
        )

    else:

        category_budget = None
        category_actual = None
        category_commitments = None
        category_projected = None
        category_remaining = None
        category_used = None
        category_decision = "NO BUDGET DATA"

    # ----------------------------------------------
    # FINAL DECISION
    # ----------------------------------------------

    risk_rank = {
        "NO BUDGET DATA": 0,
        "WITHIN BUDGET": 1,
        "CAUTION": 2,
        "HIGH RISK": 3,
        "OVER BUDGET": 4,
    }

    if category_budget is None:

        final_decision = program_decision

        reason = (
            "No verified category budget is "
            "available. Decision is based on "
            "the total program budget."
        )

    elif (
        risk_rank[category_decision]
        > risk_rank[program_decision]
    ):

        final_decision = category_decision

        reason = (
            "Category-level budget is more "
            "restrictive than total program budget."
        )

    else:

        final_decision = program_decision

        reason = (
            "Total program budget is the "
            "controlling constraint."
        )

    return {
        "program_budget":
            program_budget,

        "program_actual":
            program_actual,

        "program_commitments":
            program_commitments,

        "program_projected":
            program_projected,

        "program_remaining":
            program_remaining,

        "program_used":
            program_used,

        "program_decision":
            program_decision,

        "expense_category":
            expense_category,

        "category_budget":
            category_budget,

        "category_actual":
            category_actual,

        "category_commitments":
            category_commitments,

        "category_projected":
            category_projected,

        "category_remaining":
            category_remaining,

        "category_used":
            category_used,

        "category_decision":
            category_decision,

        "final_decision":
            final_decision,

        "reason":
            reason,
    }


# --------------------------------------------------
# DISPLAY INDIVIDUAL REQUEST
# --------------------------------------------------

def print_analysis(
    program,
    request,
    result
):

    print()
    print(
        program["program_name"]
    )

    print(
        "-" * len(
            program["program_name"]
        )
    )

    print(
        f"Request ID:               "
        f"{request['transaction_id']}"
    )

    print(
        f"Vendor:                   "
        f"{request['vendor']}"
    )

    print(
        f"Description:              "
        f"{request['description']}"
    )

    print(
        f"Expense Category:         "
        f"{result['expense_category']}"
    )

    print(
        f"Request Amount:           "
        f"${money(request['amount']):,.0f}"
    )

    print()

    print("PROGRAM-LEVEL CONTROL")
    print("---------------------")

    print(
        f"Program Budget:           "
        f"${result['program_budget']:,.0f}"
    )

    print(
        f"Actual Spend:             "
        f"${result['program_actual']:,.0f}"
    )

    print(
        f"Open Commitments:         "
        f"${result['program_commitments']:,.0f}"
    )

    print(
        f"Projected Spend:          "
        f"${result['program_projected']:,.0f}"
    )

    print(
        f"Projected Remaining:      "
        f"${result['program_remaining']:,.0f}"
    )

    print(
        f"Projected Budget Used:    "
        f"{result['program_used']:.1f}%"
    )

    print(
        f"Program Decision:         "
        f"{result['program_decision']}"
    )

    print()

    print("CATEGORY-LEVEL CONTROL")
    print("----------------------")

    if result["category_budget"] is None:

        print(
            "No verified category budget "
            "available."
        )

    else:

        print(
            f"Category Budget:          "
            f"${result['category_budget']:,.0f}"
        )

        print(
            f"Category Actual:          "
            f"${result['category_actual']:,.0f}"
        )

        print(
            f"Category Commitments:     "
            f"${result['category_commitments']:,.0f}"
        )

        print(
            f"Projected Category Spend: "
            f"${result['category_projected']:,.0f}"
        )

        print(
            f"Category Remaining:       "
            f"${result['category_remaining']:,.0f}"
        )

        print(
            f"Category Budget Used:     "
            f"{result['category_used']:.1f}%"
        )

        print(
            f"Category Decision:        "
            f"{result['category_decision']}"
        )

    print()

    print(
        f"FINAL KORBI DECISION:     "
        f"{result['final_decision']}"
    )

    print(
        f"Reason:                   "
        f"{result['reason']}"
    )


# --------------------------------------------------
# DEPARTMENT RISK SUMMARY
# --------------------------------------------------

def print_risk_summary(
    review_results
):

    risk_counts = {
        "WITHIN BUDGET": 0,
        "CAUTION": 0,
        "HIGH RISK": 0,
        "OVER BUDGET": 0,
        "NO BUDGET DATA": 0,
    }

    risk_rank = {
        "NO BUDGET DATA": 0,
        "WITHIN BUDGET": 1,
        "CAUTION": 2,
        "HIGH RISK": 3,
        "OVER BUDGET": 4,
    }

    for review in review_results:

        decision = (
            review["result"][
                "final_decision"
            ]
        )

        if decision in risk_counts:
            risk_counts[decision] += 1

    print()
    print("DEPARTMENT RISK SUMMARY")
    print("=======================")

    print(
        f"Requests Reviewed:        "
        f"{len(review_results)}"
    )

    print(
        f"Within Budget:            "
        f"{risk_counts['WITHIN BUDGET']}"
    )

    print(
        f"Caution:                  "
        f"{risk_counts['CAUTION']}"
    )

    print(
        f"High Risk:                "
        f"{risk_counts['HIGH RISK']}"
    )

    print(
        f"Over Budget:              "
        f"{risk_counts['OVER BUDGET']}"
    )

    print(
        f"No Budget Data:           "
        f"{risk_counts['NO BUDGET DATA']}"
    )

    if not review_results:
        return

    highest_risk = max(
        review_results,
        key=lambda review: (
            risk_rank.get(
                review["result"][
                    "final_decision"
                ],
                0
            ),
            review["result"][
                "category_used"
            ]
            if review["result"][
                "category_used"
            ] is not None
            else review["result"][
                "program_used"
            ]
        )
    )

    program = (
        highest_risk["program"]
    )

    request = (
        highest_risk["request"]
    )

    result = (
        highest_risk["result"]
    )

    print()
    print("HIGHEST RISK REQUEST")
    print("--------------------")

    print(
        f"Program:                  "
        f"{program['program_name']}"
    )

    print(
        f"Request ID:               "
        f"{request['transaction_id']}"
    )

    print(
        f"Description:              "
        f"{request['description']}"
    )

    print(
        f"Amount:                   "
        f"${money(request['amount']):,.0f}"
    )

    print(
        f"Decision:                 "
        f"{result['final_decision']}"
    )

    if result["category_used"] is not None:

        print(
            f"Category Budget Used:     "
            f"{result['category_used']:.1f}%"
        )

        print(
            f"Category Remaining:       "
            f"${result['category_remaining']:,.0f}"
        )

    else:

        print(
            f"Program Budget Used:      "
            f"{result['program_used']:.1f}%"
        )

        print(
            f"Program Remaining:        "
            f"${result['program_remaining']:,.0f}"
        )


# --------------------------------------------------
# RUN KORBI
# --------------------------------------------------

def run_korbi():

    budget_data = read_csv(
        BUDGET_FILE
    )

    ledger_data = read_csv(
        LEDGER_FILE
    )

    category_data = read_csv(
        CATEGORY_BUDGET_FILE
    )

    programs = get_program_budgets(
        budget_data
    )

    category_budgets = (
        get_category_budgets(
            category_data
        )
    )

    grouped = group_transactions(
        ledger_data
    )

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()

    print(
        "CATEGORY-LEVEL BUDGET CONTROL"
    )

    print(
        "============================="
    )

    print()

    print(
        "TEST MODE - Operational "
        "transactions are simulated."
    )

    print(
        "Budget controls marked VERIFIED "
        "come from the Sonoma proposed model."
    )

    review_results = []

    for program_code, transactions in (
        grouped.items()
    ):

        if program_code not in programs:

            print()
            print(
                f"WARNING: {program_code} "
                f"is not in the budget model."
            )

            continue

        program = (
            programs[
                program_code
            ]
        )

        pending_requests = (
            get_pending_requests(
                transactions
            )
        )

        for request in pending_requests:

            result = evaluate_request(
                program,
                transactions,
                request,
                category_budgets
            )

            print_analysis(
                program,
                request,
                result
            )

            review_results.append(
                {
                    "program": program,
                    "request": request,
                    "result": result,
                }
            )

    print_risk_summary(
        review_results
    )

    print()
    print("KORBI REVIEW COMPLETE")
    print("=====================")

    print(
        f"Pending Requests Reviewed: "
        f"{len(review_results)}"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    try:

        run_korbi()

    except Exception as error:

        print()
        print("KORBI ERROR")
        print("===========")
        print(error)