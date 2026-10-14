import csv
from pathlib import Path


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

BUDGET_FILE = (
    PROCESSED_FOLDER
    / "sonoma_proposed_athletics_budget.csv"
)

FUNDING_FILE = (
    PROCESSED_FOLDER
    / "sonoma_funding_model.csv"
)

STAFFING_FILE = (
    PROCESSED_FOLDER
    / "sonoma_staffing_model.csv"
)

OUTPUT_FILE = (
    PROCESSED_FOLDER
    / "sonoma_financial_model_summary.csv"
)


# --------------------------------------------------
# READ CSV
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

        return list(
            csv.DictReader(file)
        )


# --------------------------------------------------
# NUMBER HELPERS
# --------------------------------------------------

def money(value):

    if value in ["", None]:
        return 0

    return int(
        float(value)
    )


def number(value):

    if value in ["", None]:
        return 0.0

    return float(value)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():

    budget = read_csv(
        BUDGET_FILE
    )

    funding = read_csv(
        FUNDING_FILE
    )

    staffing = read_csv(
        STAFFING_FILE
    )

    return (
        budget,
        funding,
        staffing,
    )


# --------------------------------------------------
# GET BUDGET VALUE
# --------------------------------------------------

def get_budget_value(
    budget,
    program_code,
    expense_line
):

    matches = [
        row
        for row in budget
        if row["program_code"] == program_code
        and row["expense_line"] == expense_line
    ]

    if len(matches) != 1:

        raise ValueError(
            f"Expected exactly one budget record for "
            f"{program_code} / {expense_line}. "
            f"Found {len(matches)}."
        )

    return money(
        matches[0]["amount"]
    )


# --------------------------------------------------
# CALCULATE BUDGET MODEL
# --------------------------------------------------

def analyze_budget(budget):

    total_budget = get_budget_value(
        budget,
        "FULL_PROGRAM",
        "TOTAL EXPENSES"
    )

    general_budget = get_budget_value(
        budget,
        "GENERAL",
        "TOTAL EXPENSES"
    )

    total_compensation = get_budget_value(
        budget,
        "FULL_PROGRAM",
        "Total Compensation"
    )

    scholarships = get_budget_value(
        budget,
        "FULL_PROGRAM",
        "Scholarship (ALL funds)"
    )

    operating_expenses = get_budget_value(
        budget,
        "FULL_PROGRAM",
        "Operating Expenses"
    )

    total_operating = get_budget_value(
        budget,
        "FULL_PROGRAM",
        "Total Operating Expenses"
    )

    sport_specific_budget = sum(
        money(row["amount"])
        for row in budget
        if row["expense_line"] == "TOTAL EXPENSES"
        and row["program_code"]
        not in [
            "FULL_PROGRAM",
            "GENERAL",
        ]
    )

    return {
        "total_budget":
            total_budget,

        "general_budget":
            general_budget,

        "sport_specific_budget":
            sport_specific_budget,

        "total_compensation":
            total_compensation,

        "scholarships":
            scholarships,

        "operating_expenses":
            operating_expenses,

        "total_operating":
            total_operating,
    }


# --------------------------------------------------
# ANALYZE HISTORICAL FUNDING
# --------------------------------------------------

def analyze_funding(funding):

    historical = [
        row
        for row in funding
        if row["record_type"] == "FUNDING_SOURCE"
        and row["model_type"] == "HISTORICAL_FUNDING"
    ]

    historical_total = sum(
        money(row["amount"])
        for row in historical
    )

    recurring_historical = sum(
        money(row["amount"])
        for row in historical
        if row["recurring_status"]
        == "HISTORICAL_RECURRING"
    )

    one_time_historical = sum(
        money(row["amount"])
        for row in historical
        if row["recurring_status"]
        == "ONE_TIME"
    )

    other_historical = (
        historical_total
        - recurring_historical
        - one_time_historical
    )

    rebuild_records = [
        row
        for row in funding
        if row["record_type"] == "FUNDING_SOURCE"
        and row["model_type"] == "ONE_TIME_REBUILD"
    ]

    rebuild_fund = sum(
        money(row["amount"])
        for row in rebuild_records
    )

    return {
        "historical_total":
            historical_total,

        "recurring_historical":
            recurring_historical,

        "one_time_historical":
            one_time_historical,

        "other_historical":
            other_historical,

        "rebuild_fund":
            rebuild_fund,
    }


# --------------------------------------------------
# ANALYZE STAFFING
# --------------------------------------------------

def analyze_staffing(staffing):

    admin_records = [
        row
        for row in staffing
        if row["record_type"]
        == "ADMINISTRATIVE_STAFF"
    ]

    admin_positions = len(
        admin_records
    )

    admin_fte = sum(
        number(row["fte"])
        for row in admin_records
    )

    minimum_salary = sum(
        money(row["minimum_salary"])
        for row in admin_records
    )

    maximum_salary = sum(
        money(row["maximum_salary"])
        for row in admin_records
    )

    coaching_records = [
        row
        for row in staffing
        if row["record_type"]
        == "COACHING_STRUCTURE"
    ]

    coaching_head_fte = sum(
        number(row["head_coach_fte"])
        for row in coaching_records
    )

    coaching_assistant_fte = sum(
        number(row["assistant_coach_fte"])
        for row in coaching_records
    )

    return {
        "admin_positions":
            admin_positions,

        "admin_fte":
            admin_fte,

        "minimum_salary":
            minimum_salary,

        "maximum_salary":
            maximum_salary,

        "coaching_head_fte":
            coaching_head_fte,

        "coaching_assistant_fte":
            coaching_assistant_fte,
    }


# --------------------------------------------------
# BUILD FINANCIAL SUMMARY
# --------------------------------------------------

def build_summary(
    budget_analysis,
    funding_analysis,
    staffing_analysis
):

    total_budget = (
        budget_analysis[
            "total_budget"
        ]
    )

    historical_total = (
        funding_analysis[
            "historical_total"
        ]
    )

    historical_vs_proposed = (
        historical_total
        - total_budget
    )

    general_share = (
        budget_analysis[
            "general_budget"
        ]
        / total_budget
        * 100
    )

    compensation_share = (
        budget_analysis[
            "total_compensation"
        ]
        / total_budget
        * 100
    )

    scholarship_share = (
        budget_analysis[
            "scholarships"
        ]
        / total_budget
        * 100
    )

    operating_share = (
        budget_analysis[
            "operating_expenses"
        ]
        / total_budget
        * 100
    )

    summary = [

        {
            "metric":
                "Proposed Annual Athletics Budget",

            "value":
                total_budget,

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "White Paper proposed reinstated athletics budget.",
        },

        {
            "metric":
                "General / Shared Budget",

            "value":
                budget_analysis[
                    "general_budget"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Shared athletics administration and support costs.",
        },

        {
            "metric":
                "Sport-Specific Budget",

            "value":
                budget_analysis[
                    "sport_specific_budget"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Sum of individual sport TOTAL EXPENSES.",
        },

        {
            "metric":
                "General Share of Budget",

            "value":
                round(
                    general_share,
                    2
                ),

            "unit":
                "PERCENT",

            "status":
                "CALCULATED",

            "notes":
                "General budget divided by proposed total budget.",
        },

        {
            "metric":
                "Total Compensation",

            "value":
                budget_analysis[
                    "total_compensation"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Salary plus benefits.",
        },

        {
            "metric":
                "Compensation Share",

            "value":
                round(
                    compensation_share,
                    2
                ),

            "unit":
                "PERCENT",

            "status":
                "CALCULATED",

            "notes":
                "Total compensation divided by proposed budget.",
        },

        {
            "metric":
                "Scholarships",

            "value":
                budget_analysis[
                    "scholarships"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Scholarship expense across all funds.",
        },

        {
            "metric":
                "Scholarship Share",

            "value":
                round(
                    scholarship_share,
                    2
                ),

            "unit":
                "PERCENT",

            "status":
                "CALCULATED",

            "notes":
                "Scholarships divided by proposed budget.",
        },

        {
            "metric":
                "Operating Expenses",

            "value":
                budget_analysis[
                    "operating_expenses"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Operating expenses excluding scholarships.",
        },

        {
            "metric":
                "Operating Expense Share",

            "value":
                round(
                    operating_share,
                    2
                ),

            "unit":
                "PERCENT",

            "status":
                "CALCULATED",

            "notes":
                "Operating expenses divided by proposed budget.",
        },

        {
            "metric":
                "Historical FY24/25 Funding",

            "value":
                historical_total,

            "unit":
                "USD",

            "status":
                "HISTORICAL",

            "notes":
                "Historical funding sources reported by the White Paper.",
        },

        {
            "metric":
                "Historical Funding vs Proposed Budget",

            "value":
                historical_vs_proposed,

            "unit":
                "USD",

            "status":
                "COMPARISON_ONLY",

            "notes":
                (
                    "Historical FY24/25 funding minus proposed "
                    "reinstated budget. Different financial periods/models."
                ),
        },

        {
            "metric":
                "Administrative FTE",

            "value":
                staffing_analysis[
                    "admin_fte"
                ],

            "unit":
                "FTE",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Administrative/support staffing structure.",
        },

        {
            "metric":
                "Minimum Administrative Base Salaries",

            "value":
                staffing_analysis[
                    "minimum_salary"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Does not include benefits or External Affairs commission.",
        },

        {
            "metric":
                "Maximum Administrative Base Salaries",

            "value":
                staffing_analysis[
                    "maximum_salary"
                ],

            "unit":
                "USD",

            "status":
                "TASK_FORCE_PROJECTION",

            "notes":
                "Does not include benefits or External Affairs commission.",
        },

        {
            "metric":
                "One-Time Rebuild Funding",

            "value":
                funding_analysis[
                    "rebuild_fund"
                ],

            "unit":
                "USD",

            "status":
                "ONE_TIME",

            "notes":
                "Separate from annual operating budget.",
        },
    ]

    return summary


# --------------------------------------------------
# SAVE SUMMARY
# --------------------------------------------------

def save_summary(summary):

    fieldnames = [
        "metric",
        "value",
        "unit",
        "status",
        "notes",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary)


# --------------------------------------------------
# PRINT FINANCIAL MODEL
# --------------------------------------------------

def print_model(
    budget_analysis,
    funding_analysis,
    staffing_analysis
):

    total_budget = (
        budget_analysis[
            "total_budget"
        ]
    )

    print()
    print("SONOMA ATHLETICS FINANCIAL MODEL")
    print("================================")

    print()
    print("PROPOSED ANNUAL BUDGET")
    print("======================")

    print(
        f"Total Budget:             "
        f"${total_budget:,.0f}"
    )

    print(
        f"General / Shared:         "
        f"${budget_analysis['general_budget']:,.0f}"
    )

    print(
        f"Sport-Specific:           "
        f"${budget_analysis['sport_specific_budget']:,.0f}"
    )

    print()
    print("EXPENSE STRUCTURE")
    print("=================")

    print(
        f"Compensation:             "
        f"${budget_analysis['total_compensation']:,.0f}"
    )

    print(
        f"Scholarships:             "
        f"${budget_analysis['scholarships']:,.0f}"
    )

    print(
        f"Other Operating:          "
        f"${budget_analysis['operating_expenses']:,.0f}"
    )

    print()
    print("HISTORICAL FUNDING CONTEXT")
    print("==========================")

    print(
        f"FY24/25 Funding:          "
        f"${funding_analysis['historical_total']:,.0f}"
    )

    difference = (
        funding_analysis[
            "historical_total"
        ]
        - total_budget
    )

    print(
        f"Historical vs Proposed:   "
        f"${difference:,.0f}"
    )

    print()
    print(
        "WARNING: This difference is a comparison only."
    )

    print(
        "Historical FY24/25 funding and the proposed "
        "reinstated budget are not the same accounting period/model."
    )

    print()
    print("STAFFING")
    print("========")

    print(
        f"Administrative Positions: "
        f"{staffing_analysis['admin_positions']}"
    )

    print(
        f"Administrative FTE:       "
        f"{staffing_analysis['admin_fte']:.1f}"
    )

    print(
        f"Base Salary Range:        "
        f"${staffing_analysis['minimum_salary']:,.0f}"
        f" - "
        f"${staffing_analysis['maximum_salary']:,.0f}"
    )

    print()
    print("ONE-TIME REBUILD FUND")
    print("=====================")

    print(
        f"One-Time Funding:         "
        f"${funding_analysis['rebuild_fund']:,.0f}"
    )

    print(
        "This is kept separate from the annual operating model."
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    try:

        (
            budget,
            funding,
            staffing,
        ) = load_data()

        budget_analysis = (
            analyze_budget(
                budget
            )
        )

        funding_analysis = (
            analyze_funding(
                funding
            )
        )

        staffing_analysis = (
            analyze_staffing(
                staffing
            )
        )

        summary = build_summary(
            budget_analysis,
            funding_analysis,
            staffing_analysis,
        )

        save_summary(
            summary
        )

        print_model(
            budget_analysis,
            funding_analysis,
            staffing_analysis,
        )

        print()
        print("MODEL STATUS")
        print("============")

        print(
            "Successfully connected:"
        )

        print(
            "- Proposed Budget"
        )

        print(
            "- Historical Funding"
        )

        print(
            "- Staffing"
        )

        print(
            "- One-Time Rebuild Funding"
        )

        print()
        print("Saved To:")
        print(OUTPUT_FILE)

    except Exception as error:

        print()
        print("MODEL ERROR")
        print("===========")

        print(error)


if __name__ == "__main__":
    main()