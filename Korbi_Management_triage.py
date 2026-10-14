import csv
from pathlib import Path


# ============================================================
# KORBI
# Knowledge & Operations Resource for Business Intelligence
#
# MANAGEMENT TRIAGE QUEUE
#
# PURPOSE
# -------
# Allows management to review KORBI's financial recommendation
# and make the final human decision.
#
# Every request includes:
# - KORBI recommendation
# - Budget impact
# - Business impact
# - Risk assessment
# - Management suggestion
#
# KORBI does NOT automatically approve purchases.
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent

PROCESSED_FOLDER = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
)


TRIAGE_FILE = (
    PROCESSED_FOLDER
    / "korbi_bulk_triage_results.csv"
)


DECISION_FILE = (
    PROCESSED_FOLDER
    / "korbi_management_decisions.csv"
)


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

        return list(
            csv.DictReader(file)
        )


def write_csv(
    file_path,
    rows,
    fieldnames
):

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
# EXISTING DECISIONS
# ============================================================

def load_existing_decisions():

    rows = read_csv(
        DECISION_FILE
    )

    decisions = {}

    for row in rows:

        decisions[
            row["request_id"]
        ] = row

    return decisions


# ============================================================
# DECISION MENU
# ============================================================

def choose_decision():

    print()
    print("YOUR DECISION")
    print("=============")

    print("1. APPROVE")
    print("2. DENY")
    print("3. DEFER")
    print("4. ESCALATE")
    print("5. REQUEST MORE INFORMATION")
    print("6. SKIP")
    print("7. EXIT REVIEW")

    while True:

        choice = input(
            "\nEnter decision number: "
        ).strip()

        if choice == "1":
            return "APPROVE"

        if choice == "2":
            return "DENY"

        if choice == "3":
            return "DEFER"

        if choice == "4":
            return "ESCALATE"

        if choice == "5":
            return "REQUEST MORE INFORMATION"

        if choice == "6":
            return "SKIP"

        if choice == "7":
            return "EXIT"

        print(
            "Enter a number from 1-7."
        )


# ============================================================
# CATEGORY BUSINESS MEANING
# ============================================================

def category_business_context(
    row
):

    category = row.get(
        "category_code",
        ""
    )

    description = row.get(
        "description",
        ""
    )

    priority = row.get(
        "priority",
        ""
    )

    if category == "TRAV":

        return (
            "This request affects team travel and competition "
            "operations. Travel expenses are often time-sensitive "
            "because airfare, lodging, transportation, and event "
            "schedules may require commitments before the trip occurs."
        )

    if category == "MIE":

        return (
            "This request affects meals and incidental expenses "
            "associated with team travel. These costs support scheduled "
            "team movement and should be reviewed against approved "
            "travel plans, roster size, and applicable per diem policy."
        )

    if category == "EQUIP":

        if priority == "CRITICAL":

            return (
                "This request affects equipment required for safe or "
                "continuous team operations. Delaying replacement may "
                "create safety, practice, competition, or operational risk."
            )

        if priority == "NECESSARY":

            return (
                "This request addresses equipment that is worn, aging, "
                "damaged, or operationally important. Delaying the purchase "
                "may increase maintenance, reliability, or replacement risk."
            )

        return (
            "This equipment request may improve performance, efficiency, "
            "or student-athlete experience, but current operations can "
            "generally continue without immediate purchase."
        )

    if category == "TECH":

        return (
            "This request affects technology, software, analytics, or "
            "performance systems. In addition to the current purchase "
            "price, management should consider recurring subscriptions, "
            "renewal costs, implementation needs, and whether the tool "
            "creates measurable operational or competitive value."
        )

    if category == "UNIF":

        return (
            "This request affects uniforms or apparel required for team "
            "operations and competition. Management should consider current "
            "inventory, replacement cycle, roster needs, and whether the "
            "purchase is required before upcoming competition."
        )

    if category == "FAC":

        return (
            "This request affects a field, facility, or competition space. "
            "Facility work can affect safety, practice availability, event "
            "readiness, and the department's ability to host competition."
        )

    if category == "OPS":

        return (
            "This request affects team or event operations. These costs can "
            "support officials, staffing, competition delivery, equipment, "
            "or other functions required to conduct the season."
        )

    return (
        f"This request affects program operations through the proposed "
        f"purchase: {description}."
    )


# ============================================================
# BUDGET IMPACT
# ============================================================

def build_budget_impact(
    row
):

    annual_budget = safe_float(
        row["annual_budget"]
    )

    amount = safe_float(
        row["amount"]
    )

    baseline_remaining = safe_float(
        row["baseline_remaining"]
    )

    remaining_after = safe_float(
        row["remaining_with_request"]
    )

    before_percent = safe_float(
        row["baseline_percent"]
    )

    after_percent = safe_float(
        row["percent_with_request"]
    )

    request_percent = (
        amount
        / annual_budget
        * 100
        if annual_budget
        else 0
    )

    if baseline_remaining > 0:

        cushion_used = (
            amount
            / baseline_remaining
            * 100
        )

    else:

        cushion_used = 100.0

    if remaining_after < 0:

        deficit = abs(
            remaining_after
        )

        return (
            f"The {money(amount)} request represents "
            f"{request_percent:.1f}% of the program's annual operating "
            f"budget. Projected utilization would increase from "
            f"{before_percent:.1f}% to {after_percent:.1f}%. "
            f"The request would eliminate the remaining budget cushion "
            f"and create a projected deficit of {money(deficit)}."
        )

    return (
        f"The {money(amount)} request represents "
        f"{request_percent:.1f}% of the program's annual operating "
        f"budget. Projected utilization would increase from "
        f"{before_percent:.1f}% to {after_percent:.1f}%. "
        f"The remaining projected cushion would decrease from "
        f"{money(baseline_remaining)} to {money(remaining_after)}. "
        f"The request would consume approximately "
        f"{cushion_used:.1f}% of the program's current remaining "
        f"financial flexibility."
    )


# ============================================================
# BUSINESS IMPACT
# ============================================================

def build_business_impact(
    row
):

    context = (
        category_business_context(
            row
        )
    )

    priority = row.get(
        "priority",
        ""
    )

    justification = row.get(
        "business_justification",
        ""
    )

    season = row.get(
        "season",
        ""
    )

    extra = ""

    if priority == "CRITICAL":

        extra = (
            " The request is classified as CRITICAL, meaning delay may "
            "affect safety, competition, continuity, or another essential "
            "operating requirement."
        )

    elif priority == "NECESSARY":

        extra = (
            " The request is classified as NECESSARY, meaning the purchase "
            "addresses a legitimate replacement, reliability, or preventive "
            "operating need."
        )

    elif priority == "ENHANCEMENT":

        extra = (
            " The request is classified as an ENHANCEMENT, so the potential "
            "benefit should be weighed against preserving funds for required "
            "seasonal obligations."
        )

    season_context = ""

    if season == "FALL":

        season_context = (
            " The program is currently in its active fall competition "
            "period, so additional travel and competition-related costs "
            "may still emerge."
        )

    elif season == "WINTER":

        season_context = (
            " The program is approaching its primary winter competition "
            "period, meaning a significant portion of season costs remains "
            "ahead."
        )

    elif season == "SPRING":

        season_context = (
            " The program's primary competitive season is still ahead, so "
            "current remaining funds must also support future spring travel, "
            "competition, and operating needs."
        )

    elif season == "FALL_SPRING":

        season_context = (
            " The program carries activity across both fall and spring, so "
            "the remaining budget must support obligations in both portions "
            "of the competitive year."
        )

    return (
        f"{context}{extra}{season_context} "
        f"The stated business justification is: {justification}"
    )


# ============================================================
# RISK SUMMARY
# ============================================================

def build_risk_summary(
    row
):

    after_percent = safe_float(
        row["percent_with_request"]
    )

    remaining = safe_float(
        row["remaining_with_request"]
    )

    priority = row.get(
        "priority",
        ""
    )

    if after_percent > 100:

        return (
            "HIGH FINANCIAL RISK. Approval would place the program "
            "over its projected annual operating budget. Any approval "
            "should require an offsetting reduction, transfer, alternative "
            "funding source, or documented budget adjustment."
        )

    if after_percent >= 95:

        return (
            "HIGH FINANCIAL RISK. Approval would leave very limited "
            f"flexibility, with only {money(remaining)} projected to remain. "
            "Unexpected travel, competition, equipment, or operational "
            "costs could place the program over budget."
        )

    if after_percent >= 90:

        return (
            "MODERATE-HIGH FINANCIAL RISK. The request remains within "
            "budget, but the program would move into the caution range. "
            "Management should verify remaining seasonal obligations "
            "before committing funds."
        )

    if after_percent >= 80:

        if priority == "ENHANCEMENT":

            return (
                "MODERATE FINANCIAL RISK. The program remains within "
                "budget, but the request is discretionary and would reduce "
                "flexibility available for required costs later in the year."
            )

        return (
            "MODERATE FINANCIAL RISK. The purchase fits within the current "
            "forecast, but management should continue monitoring remaining "
            "seasonal expenses."
        )

    return (
        "LOWER FINANCIAL RISK. The current forecast indicates adequate "
        "capacity remains after the request, although normal procurement "
        "and operational review should still be completed."
    )


# ============================================================
# ACTIONABLE KORBI RECOMMENDATION
# ============================================================

def build_actionable_recommendation(
    row
):

    after_percent = safe_float(
        row["percent_with_request"]
    )

    remaining = safe_float(
        row["remaining_with_request"]
    )

    amount = safe_float(
        row["amount"]
    )

    priority = row.get(
        "priority",
        ""
    )

    category = row.get(
        "category_code",
        ""
    )

    # --------------------------------------------------------
    # OVER BUDGET
    # --------------------------------------------------------

    if after_percent > 100:

        if priority == "CRITICAL":

            return (
                "ESCALATE — CRITICAL NEED REQUIRES A FUNDING SOURCE",
                (
                    f"Do not fund the {money(amount)} request from the "
                    "current operating allocation without identifying an "
                    "offset, transfer, or alternative funding source. "
                    "Because the need is critical, escalate rather than "
                    "simply denying the operational requirement."
                ),
            )

        return (
            "DENY OR DEFER — REQUEST CREATES A PROJECTED DEFICIT",
            (
                f"Do not approve the request from the current operating "
                f"budget. Identify savings, reduce the scope of the purchase, "
                f"move the expenditure to another appropriate funding source, "
                f"or reconsider later if the forecast improves."
            ),
        )

    # --------------------------------------------------------
    # 95-100%
    # --------------------------------------------------------

    if after_percent >= 95:

        if priority == "CRITICAL":

            return (
                "APPROVE ONLY WITH SENIOR MANAGEMENT REVIEW",
                (
                    f"The critical need may justify the purchase, but approval "
                    f"would leave only {money(remaining)} in projected "
                    f"capacity. Confirm all remaining season obligations and "
                    f"identify contingency funding before final approval."
                ),
            )

        if priority == "NECESSARY":

            return (
                "DEFER UNLESS OFFSETTING SAVINGS ARE IDENTIFIED",
                (
                    f"The request addresses a legitimate operating need, but "
                    f"approval would leave only {money(remaining)} available. "
                    f"Confirm remaining obligations or identify savings equal "
                    f"to at least {money(amount)} before approving."
                ),
            )

        return (
            "DEFER — PRESERVE REMAINING BUDGET CAPACITY",
            (
                "The request is an enhancement and approval would leave too "
                "little flexibility for required seasonal costs. Reconsider "
                "if documented savings develop later in the year."
            ),
        )

    # --------------------------------------------------------
    # 90-95%
    # --------------------------------------------------------

    if after_percent >= 90:

        if priority == "CRITICAL":

            return (
                "APPROVE — MONITOR REMAINING OBLIGATIONS",
                (
                    "The request supports a critical need and remains within "
                    "budget. Approve after confirming that scheduled travel, "
                    "competition, and other required costs remain funded."
                ),
            )

        if priority == "NECESSARY":

            return (
                "APPROVE ONLY AFTER REMAINING COSTS ARE CONFIRMED",
                (
                    "The need appears legitimate, but the program would move "
                    "into a tight financial position. Confirm remaining season "
                    "costs before issuing the purchase."
                ),
            )

        return (
            "DEFER — BUSINESS VALUE DOES NOT OUTWEIGH CURRENT BUDGET RISK",
            (
                "The enhancement would materially reduce year-end flexibility. "
                "Reevaluate after additional actual expenses post or savings "
                "are identified."
            ),
        )

    # --------------------------------------------------------
    # 80-90%
    # --------------------------------------------------------

    if after_percent >= 80:

        if priority == "CRITICAL":

            return (
                "APPROVE — ADEQUATE CAPACITY REMAINS",
                (
                    "The request addresses a critical operating need and the "
                    "program retains reasonable forecasted capacity afterward."
                ),
            )

        if priority == "NECESSARY":

            return (
                "APPROVE WITH BUDGET MONITORING",
                (
                    "The purchase addresses a necessary operating need and "
                    "fits within the current forecast. Continue monitoring "
                    "seasonal obligations after approval."
                ),
            )

        return (
            "CONSIDER — REQUIRE CLEAR OPERATIONAL VALUE",
            (
                "The enhancement fits financially, but approval should depend "
                "on whether the expected benefit is worth reducing the "
                "program's remaining flexibility."
            ),
        )

    # --------------------------------------------------------
    # BELOW 80%
    # --------------------------------------------------------

    if priority == "CRITICAL":

        return (
            "APPROVE — FINANCIAL CAPACITY SUPPORTS THE NEED",
            (
                "The request addresses a critical operational requirement and "
                "the current forecast indicates adequate capacity remains."
            ),
        )

    if priority == "NECESSARY":

        return (
            "APPROVE — FINANCIAL CAPACITY REMAINS HEALTHY",
            (
                "The purchase addresses a necessary operating requirement and "
                "the program retains a healthy projected cushion afterward."
            ),
        )

    if category == "TECH":

        return (
            "CONSIDER — VERIFY VALUE AND RECURRING COSTS",
            (
                "The program has financial capacity for the enhancement. "
                "Before approval, confirm measurable benefit and any future "
                "subscription, licensing, or renewal costs."
            ),
        )

    return (
        "CONSIDER — FINANCIALLY AFFORDABLE",
        (
            "The program currently has sufficient forecasted capacity. "
            "Approval should depend on the operational value of the request "
            "relative to other potential uses of the remaining budget."
        ),
    )


# ============================================================
# DISPLAY REQUEST
# ============================================================

def display_request(
    row,
    number,
    total
):

    budget_impact = (
        build_budget_impact(
            row
        )
    )

    business_impact = (
        build_business_impact(
            row
        )
    )

    risk_summary = (
        build_risk_summary(
            row
        )
    )

    (
        actionable_recommendation,
        management_suggestion
    ) = build_actionable_recommendation(
        row
    )

    print()
    print("=" * 68)

    print(
        f"REQUEST {number} OF {total}"
    )

    print("=" * 68)

    print()

    print(
        f"Request ID:        "
        f"{row['request_id']}"
    )

    print(
        f"Program:           "
        f"{row['program_name']}"
    )

    print(
        f"Category:          "
        f"{row['category_code']} - "
        f"{row['category_name']}"
    )

    print(
        f"Request:           "
        f"{row['description']}"
    )

    print(
        f"Vendor:            "
        f"{row['vendor']}"
    )

    print(
        f"Priority:          "
        f"{row['priority']}"
    )

    print(
        f"Amount:            "
        f"{money(row['amount'])}"
    )

    print()

    print("BUSINESS JUSTIFICATION")
    print("----------------------")

    print(
        row[
            "business_justification"
        ]
    )

    print()

    print("PROGRAM FINANCIAL POSITION")
    print("--------------------------")

    print(
        f"Annual Budget:      "
        f"{money(row['annual_budget'])}"
    )

    print(
        f"Q1 Actuals:         "
        f"{money(row['q1_actuals'])}"
    )

    print(
        f"Open POs:           "
        f"{money(row['open_pos'])}"
    )

    print(
        f"Scheduled Future:   "
        f"{money(row['scheduled_future'])}"
    )

    print(
        f"Expected Future:    "
        f"{money(row['expected_future'])}"
    )

    print()

    print("BUDGET BEFORE REQUEST")
    print("---------------------")

    print(
        f"Projected Spend:    "
        f"{money(row['baseline_projected'])}"
    )

    print(
        f"Remaining Cushion:  "
        f"{money(row['baseline_remaining'])}"
    )

    print(
        f"Budget Used:        "
        f"{percent(row['baseline_percent'])}"
    )

    print()

    print("BUDGET AFTER REQUEST")
    print("--------------------")

    print(
        f"Projected Spend:    "
        f"{money(row['projected_with_request'])}"
    )

    print(
        f"Remaining Cushion:  "
        f"{money(row['remaining_with_request'])}"
    )

    print(
        f"Budget Used:        "
        f"{percent(row['percent_with_request'])}"
    )

    print(
        f"Financial Status:   "
        f"{row['financial_status']}"
    )

    print()

    print("KORBI RECOMMENDATION")
    print("--------------------")

    print(
        actionable_recommendation
    )

    print()

    print("BUDGET IMPACT")
    print("-------------")

    print(
        budget_impact
    )

    print()

    print("BUSINESS IMPACT")
    print("---------------")

    print(
        business_impact
    )

    print()

    print("RISK ASSESSMENT")
    print("---------------")

    print(
        risk_summary
    )

    print()

    print("KORBI SUGGESTION")
    print("----------------")

    print(
        management_suggestion
    )

    return {
        "budget_impact":
            budget_impact,

        "business_impact":
            business_impact,

        "risk_summary":
            risk_summary,

        "actionable_recommendation":
            actionable_recommendation,

        "management_suggestion":
            management_suggestion,
    }


# ============================================================
# CREATE DECISION RECORD
# ============================================================

def create_decision_record(
    row,
    analysis,
    decision,
    reviewer,
    notes
):

    return {

        "request_id":
            row["request_id"],

        "program_code":
            row["program_code"],

        "program_name":
            row["program_name"],

        "category_code":
            row["category_code"],

        "description":
            row["description"],

        "priority":
            row["priority"],

        "amount":
            row["amount"],

        "korbi_recommendation":
            analysis[
                "actionable_recommendation"
            ],

        "financial_status":
            row["financial_status"],

        "annual_budget":
            row["annual_budget"],

        "baseline_projected":
            row["baseline_projected"],

        "baseline_remaining":
            row["baseline_remaining"],

        "baseline_percent":
            row["baseline_percent"],

        "projected_with_request":
            row["projected_with_request"],

        "remaining_with_request":
            row["remaining_with_request"],

        "percent_with_request":
            row["percent_with_request"],

        "budget_impact_summary":
            analysis[
                "budget_impact"
            ],

        "business_impact_summary":
            analysis[
                "business_impact"
            ],

        "risk_summary":
            analysis[
                "risk_summary"
            ],

        "korbi_management_suggestion":
            analysis[
                "management_suggestion"
            ],

        "manager_decision":
            decision,

        "reviewed_by":
            reviewer,

        "review_date":
            SIMULATION_DATE,

        "manager_notes":
            notes,
    }


# ============================================================
# SAVE DECISIONS
# ============================================================

def save_decisions(
    decisions
):

    rows = list(
        decisions.values()
    )

    write_csv(
        DECISION_FILE,
        rows,
        DECISION_FIELDS
    )


# ============================================================
# MANAGEMENT SUMMARY
# ============================================================

def display_summary(
    decisions
):

    print()
    print("MANAGEMENT REVIEW SUMMARY")
    print("=========================")

    if not decisions:

        print()
        print(
            "No management decisions saved."
        )

        return

    counts = {}

    total_amount = 0
    approved_amount = 0
    denied_amount = 0
    deferred_amount = 0

    for row in decisions.values():

        decision = (
            row["manager_decision"]
        )

        amount = safe_float(
            row["amount"]
        )

        total_amount += amount

        counts[decision] = (
            counts.get(
                decision,
                0
            )
            + 1
        )

        if decision == "APPROVE":

            approved_amount += amount

        elif decision == "DENY":

            denied_amount += amount

        elif decision == "DEFER":

            deferred_amount += amount

    print()

    print(
        f"Requests Reviewed:   "
        f"{len(decisions)}"
    )

    print(
        f"Value Reviewed:      "
        f"{money(total_amount)}"
    )

    print(
        f"Value Approved:      "
        f"{money(approved_amount)}"
    )

    print(
        f"Value Denied:        "
        f"{money(denied_amount)}"
    )

    print(
        f"Value Deferred:      "
        f"{money(deferred_amount)}"
    )

    print()

    for decision in [
        "APPROVE",
        "DENY",
        "DEFER",
        "ESCALATE",
        "REQUEST MORE INFORMATION",
    ]:

        print(
            f"{decision}: "
            f"{counts.get(decision, 0)}"
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
        "ATHLETICS MANAGEMENT TRIAGE QUEUE"
    )

    triage_rows = read_csv(
        TRIAGE_FILE
    )

    if not triage_rows:

        raise FileNotFoundError(
            f"No triage results found:\n"
            f"{TRIAGE_FILE}"
        )

    decisions = (
        load_existing_decisions()
    )

    pending = [
        row
        for row in triage_rows
        if row["request_id"]
        not in decisions
    ]

    print()

    print(
        f"Total Triaged Requests: "
        f"{len(triage_rows)}"
    )

    print(
        f"Already Reviewed:       "
        f"{len(decisions)}"
    )

    print(
        f"Awaiting Review:        "
        f"{len(pending)}"
    )

    if not pending:

        print()
        print(
            "All requests have already "
            "been reviewed."
        )

        display_summary(
            decisions
        )

        return

    reviewer = input(
        "\nReviewer name: "
    ).strip()

    if not reviewer:

        reviewer = (
            "Management Reviewer"
        )

    for index, row in enumerate(
        pending,
        start=1
    ):

        analysis = (
            display_request(
                row,
                index,
                len(pending)
            )
        )

        decision = (
            choose_decision()
        )

        if decision == "EXIT":

            print()
            print(
                "REVIEW SESSION ENDED"
            )

            break

        if decision == "SKIP":

            print()
            print(
                "Request skipped. "
                "No decision saved."
            )

            continue

        notes = input(
            "\nDecision notes: "
        ).strip()

        print()
        print("DECISION REVIEW")
        print("===============")

        print(
            f"Request: "
            f"{row['request_id']}"
        )

        print(
            f"KORBI:   "
            f"{analysis['actionable_recommendation']}"
        )

        print(
            f"You:     "
            f"{decision}"
        )

        print(
            f"Notes:   "
            f"{notes}"
        )

        while True:

            confirm = input(
                "\nSave this decision? "
                "(Y/N): "
            ).strip().upper()

            if confirm == "Y":

                record = (
                    create_decision_record(
                        row,
                        analysis,
                        decision,
                        reviewer,
                        notes
                    )
                )

                decisions[
                    row["request_id"]
                ] = record

                save_decisions(
                    decisions
                )

                print()
                print(
                    "DECISION SAVED"
                )

                print(
                    "=============="
                )

                break

            if confirm == "N":

                print()
                print(
                    "Decision not saved."
                )

                break

            print(
                "Enter Y or N."
            )

    display_summary(
        decisions
    )

    print()
    print("DECISION FILE")
    print("=============")

    print(
        DECISION_FILE
    )

    print()
    print(
        "Management decisions do not "
        "automatically create purchase orders."
    )


if __name__ == "__main__":

    try:

        run()

    except Exception as error:

        print()
        print(
            "KORBI MANAGEMENT TRIAGE ERROR"
        )

        print(
            "============================="
        )

        print(error)