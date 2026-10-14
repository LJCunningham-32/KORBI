import csv
from pathlib import Path


# --------------------------------------------------
# KORBI BUDGET VALIDATOR
# Knowledge & Operations Resource
# for Business Intelligence
#
# Purpose:
# Validate KORBI operating category budgets against
# the structured Sonoma White Paper budget dataset.
# --------------------------------------------------


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

SOURCE_BUDGET_FILE = (
    PROCESSED_FOLDER
    / "sonoma_proposed_athletics_budget.csv"
)

KORBI_CATEGORY_FILE = (
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
# LOAD WHITE PAPER OPERATING BUDGETS
# --------------------------------------------------

def load_source_operating_budgets(rows):

    budgets = {}

    for row in rows:

        if row["expense_line"] != "Operating Expenses":
            continue

        program_code = row["program_code"]

        budgets[program_code] = {
            "program_name":
                row["program_name"],

            "source_amount":
                money(row["amount"]),
        }

    return budgets


# --------------------------------------------------
# LOAD KORBI CATEGORY BUDGETS
# --------------------------------------------------

def load_korbi_budgets(rows):

    budgets = {}

    for row in rows:

        if (
            row["expense_category"]
            != "GENERAL_OPERATING"
        ):
            continue

        program_code = row["program_code"]

        budgets[program_code] = {
            "program_name":
                row["program_name"],

            "korbi_amount":
                money(
                    row["category_budget"]
                ),

            "status":
                row["budget_status"],

            "source":
                row["source"],
        }

    return budgets


# --------------------------------------------------
# VALIDATE INDIVIDUAL PROGRAMS
# --------------------------------------------------

def validate_programs(
    source_budgets,
    korbi_budgets
):

    results = []

    all_codes = sorted(
        set(source_budgets.keys())
        | set(korbi_budgets.keys())
    )

    for code in all_codes:

        source = source_budgets.get(
            code
        )

        korbi = korbi_budgets.get(
            code
        )

        # ------------------------------------------
        # PRESENT IN SOURCE BUT NOT KORBI
        # ------------------------------------------

        if source and not korbi:

            results.append(
                {
                    "program_code":
                        code,

                    "program_name":
                        source["program_name"],

                    "source_amount":
                        source["source_amount"],

                    "korbi_amount":
                        None,

                    "difference":
                        None,

                    "validation":
                        "MISSING FROM KORBI",
                }
            )

            continue

        # ------------------------------------------
        # PRESENT IN KORBI BUT NOT SOURCE
        # ------------------------------------------

        if korbi and not source:

            results.append(
                {
                    "program_code":
                        code,

                    "program_name":
                        korbi["program_name"],

                    "source_amount":
                        None,

                    "korbi_amount":
                        korbi["korbi_amount"],

                    "difference":
                        None,

                    "validation":
                        "NOT FOUND IN SOURCE",
                }
            )

            continue

        # ------------------------------------------
        # COMPARE VALUES
        # ------------------------------------------

        source_amount = (
            source["source_amount"]
        )

        korbi_amount = (
            korbi["korbi_amount"]
        )

        difference = (
            korbi_amount
            - source_amount
        )

        if difference == 0:

            validation = "MATCH"

        else:

            validation = "MISMATCH"

        results.append(
            {
                "program_code":
                    code,

                "program_name":
                    source["program_name"],

                "source_amount":
                    source_amount,

                "korbi_amount":
                    korbi_amount,

                "difference":
                    difference,

                "validation":
                    validation,
            }
        )

    return results


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

def print_validation(
    results
):

    match_count = 0
    mismatch_count = 0
    missing_count = 0

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()

    print("BUDGET DATA VALIDATION")
    print("======================")

    print()

    print(
        "Comparing KORBI category budgets "
        "against the structured Sonoma "
        "White Paper dataset."
    )

    for result in results:

        validation = (
            result["validation"]
        )

        if validation == "MATCH":
            match_count += 1

        elif validation == "MISMATCH":
            mismatch_count += 1

        else:
            missing_count += 1

        print()
        print(
            result["program_name"]
        )

        print(
            "-" * len(
                result["program_name"]
            )
        )

        print(
            f"Program Code:             "
            f"{result['program_code']}"
        )

        if (
            result["source_amount"]
            is not None
        ):

            print(
                f"White Paper Budget:       "
                f"${result['source_amount']:,.0f}"
            )

        else:

            print(
                "White Paper Budget:       "
                "NOT FOUND"
            )

        if (
            result["korbi_amount"]
            is not None
        ):

            print(
                f"KORBI Budget:             "
                f"${result['korbi_amount']:,.0f}"
            )

        else:

            print(
                "KORBI Budget:             "
                "NOT FOUND"
            )

        if (
            result["difference"]
            is not None
        ):

            print(
                f"Difference:               "
                f"${result['difference']:,.0f}"
            )

        print(
            f"Validation:               "
            f"{validation}"
        )

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    print()
    print("VALIDATION SUMMARY")
    print("==================")

    print(
        f"Records Reviewed:         "
        f"{len(results)}"
    )

    print(
        f"Matches:                  "
        f"{match_count}"
    )

    print(
        f"Mismatches:               "
        f"{mismatch_count}"
    )

    print(
        f"Missing / Unresolved:     "
        f"{missing_count}"
    )


# --------------------------------------------------
# TOTAL RECONCILIATION
# --------------------------------------------------

def print_total_reconciliation(
    source_budgets,
    korbi_budgets
):

    # Exclude FULL PROGRAM and GENERAL from the
    # sport-specific KORBI total.

    sport_codes = [
        "MBB",
        "WBB",
        "MGO",
        "WGO",
        "MSO",
        "WSO",
        "MTF",
        "WTF",
        "MCC",
        "WCC",
        "WVB",
    ]

    korbi_sport_total = sum(
        korbi_budgets[code][
            "korbi_amount"
        ]
        for code in sport_codes
        if code in korbi_budgets
    )

    source_sport_total = sum(
        source_budgets[code][
            "source_amount"
        ]
        for code in sport_codes
        if code in source_budgets
    )

    print()
    print("SPORT OPERATING RECONCILIATION")
    print("==============================")

    print(
        f"White Paper Sport Total:  "
        f"${source_sport_total:,.0f}"
    )

    print(
        f"KORBI Sport Total:        "
        f"${korbi_sport_total:,.0f}"
    )

    print(
        f"Difference:               "
        f"${korbi_sport_total - source_sport_total:,.0f}"
    )

    if (
        korbi_sport_total
        == source_sport_total
    ):

        print(
            "Status:                   MATCH"
        )

    else:

        print(
            "Status:                   MISMATCH"
        )


# --------------------------------------------------
# RUN VALIDATION
# --------------------------------------------------

def run_validator():

    source_rows = read_csv(
        SOURCE_BUDGET_FILE
    )

    korbi_rows = read_csv(
        KORBI_CATEGORY_FILE
    )

    source_budgets = (
        load_source_operating_budgets(
            source_rows
        )
    )

    korbi_budgets = (
        load_korbi_budgets(
            korbi_rows
        )
    )

    results = validate_programs(
        source_budgets,
        korbi_budgets
    )

    print_validation(
        results
    )

    print_total_reconciliation(
        source_budgets,
        korbi_budgets
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    try:

        run_validator()

    except Exception as error:

        print()
        print("KORBI VALIDATION ERROR")
        print("======================")
        print(error)