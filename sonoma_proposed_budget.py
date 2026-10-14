import csv
from pathlib import Path


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "sonoma_proposed_athletics_budget.csv"
)


# --------------------------------------------------
# SOURCE INFORMATION
# --------------------------------------------------

SOURCE_FILE = "SSU_ATHLETICS_WHITE_PAPER_2026.pdf"
SOURCE_PAGE = 7

SOURCE_SECTION = (
    "Chapter 3: Projected Expense Budget of the "
    "Intercollegiate Athletics Department"
)

SOURCE_TABLE = (
    "ATHLETIC PROGRAM EXPENSE BUDGET SUMMARY: "
    "7 Women's and 6 Men's Sports"
)

DATA_STATUS = "VERIFIED_FROM_SOURCE_TABLE"


# --------------------------------------------------
# PROGRAM COLUMNS
# --------------------------------------------------

PROGRAMS = [
    ("FULL_PROGRAM", "Full Program"),
    ("GENERAL", "General"),
    ("MBB", "Men's Basketball"),
    ("WBB", "Women's Basketball"),
    ("MGO", "Men's Golf"),
    ("WGO", "Women's Golf"),
    ("MSO", "Men's Soccer"),
    ("WSO", "Women's Soccer"),
    ("MTF", "Men's Track & Field"),
    ("WTF", "Women's Track & Field"),
    ("MCC", "Men's Cross Country"),
    ("WCC", "Women's Cross Country"),
    ("WVB", "Women's Volleyball"),
]


# --------------------------------------------------
# SOURCE TABLE VALUES
# --------------------------------------------------

BUDGET_ROWS = {

    "Administrator Salary": [
        595956, 595956, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],

    "Faculty Salary": [
        1391184, 80544, 192624, 192624, 77448, 77448,
        192624, 192624, 48156, 48156, 48156, 48156, 192624
    ],

    "Staff Salary": [
        240132, 240132, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],

    "Student Assistants": [
        40000, 40000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ],

    "Total Salary": [
        2267272, 956632, 192624, 192624, 77448, 77448,
        192624, 192624, 48156, 48156, 48156, 48156, 192624
    ],

    "Total Benefits": [
        1380909, 568312, 119427, 119427, 48018, 48018,
        119427, 119427, 29857, 29857, 29857, 29857, 119427
    ],

    "Total Compensation": [
        3648181, 1524944, 312051, 312051, 125466, 125466,
        312051, 312051, 78013, 78013, 78013, 78013, 312051
    ],

    "Scholarship (ALL funds)": [
        895295, 14500, 165400, 148000, 74976, 97024,
        74000, 80000, 2000, 2000, 56800, 56800, 123795
    ],

    "Operating Expenses": [
        1517248, 335615, 149318, 131987, 126797, 119751,
        113069, 120347, 95316, 95316, 52331, 52331, 125068
    ],

    "Total Operating Expenses": [
        2412543, 350115, 314718, 279987, 201773, 216775,
        187069, 200347, 97316, 97316, 109131, 109131, 248863
    ],

    "TOTAL EXPENSES": [
        6060723, 1875059, 626769, 592038, 327239, 342241,
        499120, 512398, 175329, 175329, 187144, 187144, 560914
    ],
}


# --------------------------------------------------
# OPERATING METRICS
# --------------------------------------------------

FTE = [
    24, 10.50, 2.00, 2.00, 0.75, 0.75,
    2.00, 2.00, 0.50, 0.50, 0.50, 0.50, 2.00
]

TARGET_ROSTER = [
    186, 0, 14, 14, 10, 10,
    30, 30, 20, 20, 10, 10, 18
]

COST_PER_SA = [
    None, None, 44769, 42288, 32724, 34224,
    16637, 17080, 8766, 8766, 18714, 18714, 31162
]


# --------------------------------------------------
# CLASSIFY ROW
# --------------------------------------------------

def classify_row(row_name):

    if row_name in [
        "Administrator Salary",
        "Faculty Salary",
        "Staff Salary",
        "Student Assistants",
        "Total Salary",
        "Total Benefits",
        "Total Compensation",
    ]:
        return "COMPENSATION"

    if row_name == "Scholarship (ALL funds)":
        return "SCHOLARSHIPS"

    if row_name in [
        "Operating Expenses",
        "Total Operating Expenses",
    ]:
        return "OPERATING"

    if row_name == "TOTAL EXPENSES":
        return "TOTAL"

    return "OTHER"


# --------------------------------------------------
# BUILD RECORDS
# --------------------------------------------------

def build_records():

    records = []

    for row_name, values in BUDGET_ROWS.items():

        category = classify_row(row_name)

        for index, value in enumerate(values):

            program_code = PROGRAMS[index][0]
            program_name = PROGRAMS[index][1]

            notes = ""

            if program_code == "GENERAL":
                notes = (
                    "General includes Athletic Administration, "
                    "Strength and Conditioning, Sports Information, "
                    "Compliance, Events, Training, and cancelled sports."
                )

            if (
                program_code == "FULL_PROGRAM"
                and row_name == "TOTAL EXPENSES"
            ):
                notes = (
                    "White Paper reports $6,060,723. "
                    "Component totals reconcile to $6,060,724, "
                    "creating a $1 source variance."
                )

            records.append({
                "institution": "Sonoma State University",
                "budget_model": "Proposed Reinstated Athletics",
                "program_code": program_code,
                "program_name": program_name,
                "expense_category": category,
                "expense_line": row_name,
                "amount": value,
                "source_file": SOURCE_FILE,
                "source_page": SOURCE_PAGE,
                "source_section": SOURCE_SECTION,
                "source_table": SOURCE_TABLE,
                "verification_status": DATA_STATUS,
                "notes": notes,
            })

    return records


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_budget():

    warnings = []
    errors = []

    expected_columns = len(PROGRAMS)

    for row_name, values in BUDGET_ROWS.items():

        if len(values) != expected_columns:

            errors.append(
                f"{row_name}: expected {expected_columns} values, "
                f"found {len(values)}"
            )

    calculated_salary = (
        BUDGET_ROWS["Administrator Salary"][0]
        + BUDGET_ROWS["Faculty Salary"][0]
        + BUDGET_ROWS["Staff Salary"][0]
        + BUDGET_ROWS["Student Assistants"][0]
    )

    reported_salary = BUDGET_ROWS["Total Salary"][0]

    if calculated_salary != reported_salary:

        errors.append(
            "Full Program Total Salary does not reconcile."
        )

    calculated_compensation = (
        BUDGET_ROWS["Total Salary"][0]
        + BUDGET_ROWS["Total Benefits"][0]
    )

    reported_compensation = (
        BUDGET_ROWS["Total Compensation"][0]
    )

    if calculated_compensation != reported_compensation:

        errors.append(
            "Full Program Total Compensation does not reconcile."
        )

    calculated_operating = (
        BUDGET_ROWS["Scholarship (ALL funds)"][0]
        + BUDGET_ROWS["Operating Expenses"][0]
    )

    reported_operating = (
        BUDGET_ROWS["Total Operating Expenses"][0]
    )

    if calculated_operating != reported_operating:

        errors.append(
            "Full Program Total Operating Expenses does not reconcile."
        )

    calculated_total = (
        BUDGET_ROWS["Total Compensation"][0]
        + BUDGET_ROWS["Total Operating Expenses"][0]
    )

    reported_total = (
        BUDGET_ROWS["TOTAL EXPENSES"][0]
    )

    total_variance = (
        calculated_total - reported_total
    )

    if total_variance != 0:

        warnings.append(
            f"Source table TOTAL EXPENSES variance: "
            f"${total_variance:,.0f}. "
            f"Calculated ${calculated_total:,.0f} vs "
            f"reported ${reported_total:,.0f}."
        )

    component_total = sum(
        BUDGET_ROWS["TOTAL EXPENSES"][1:]
    )

    component_variance = (
        component_total - reported_total
    )

    if component_variance != 0:

        warnings.append(
            f"General + sport TOTAL EXPENSES variance: "
            f"${component_variance:,.0f}. "
            f"Components ${component_total:,.0f} vs "
            f"reported Full Program ${reported_total:,.0f}."
        )

    return errors, warnings


# --------------------------------------------------
# SAVE RECORDS
# --------------------------------------------------

def save_records(records):

    fieldnames = [
        "institution",
        "budget_model",
        "program_code",
        "program_name",
        "expense_category",
        "expense_line",
        "amount",
        "source_file",
        "source_page",
        "source_section",
        "source_table",
        "verification_status",
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
        writer.writerows(records)


# --------------------------------------------------
# PROGRAM SUMMARY
# --------------------------------------------------

def show_program_summary():

    print()
    print("PROPOSED PROGRAM BUDGET")
    print("=======================")

    totals = BUDGET_ROWS["TOTAL EXPENSES"]

    for index, program in enumerate(PROGRAMS):

        code = program[0]
        name = program[1]
        amount = totals[index]

        print(
            f"{code:<12} "
            f"{name:<25} "
            f"${amount:>12,.0f}"
        )


# --------------------------------------------------
# OPERATING METRICS
# --------------------------------------------------

def show_operating_metrics():

    print()
    print("ROSTER / STAFFING METRICS")
    print("=========================")

    for index, program in enumerate(PROGRAMS):

        code = program[0]
        name = program[1]
        fte = FTE[index]
        roster = TARGET_ROSTER[index]
        cost_per_sa = COST_PER_SA[index]

        if cost_per_sa is None:
            cost_display = "N/A"
        else:
            cost_display = f"${cost_per_sa:,.0f}"

        print(
            f"{code:<12} "
            f"{name:<25} "
            f"FTE: {fte:<6} "
            f"Roster: {roster:<4} "
            f"Cost/SA: {cost_display}"
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print()
    print("SONOMA PROPOSED ATHLETICS BUDGET")
    print("================================")

    errors, warnings = validate_budget()

    if errors:

        print()
        print("VALIDATION FAILED")
        print("=================")

        for error in errors:
            print(f"- {error}")

        print()
        print("CSV NOT CREATED.")
        return

    print()
    print("SOURCE TABLE VALIDATION: PASS")

    if warnings:

        print()
        print("SOURCE WARNINGS")
        print("===============")

        for warning in warnings:
            print(f"- {warning}")

    records = build_records()

    save_records(records)

    print()
    print(
        f"Structured Budget Records: "
        f"{len(records):,}"
    )

    print()
    print("Saved To:")
    print(OUTPUT_FILE)

    show_program_summary()
    show_operating_metrics()


if __name__ == "__main__":
    main()