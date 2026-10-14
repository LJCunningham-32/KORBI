import csv
from datetime import date
from pathlib import Path


# ============================================================
# KORBI
# Knowledge & Operations Resource for Business Intelligence
#
# PURCHASE REQUEST + FINANCIAL RECOMMENDATION ENGINE
#
# Current simulation position:
# October 1, 2027
#
# KORBI evaluates:
# - Annual sport operating budget
# - Q1 actuals
# - Open POs
# - Scheduled future expenses
# - Expected future expenses
# - Existing pending purchase requests
# - New purchase request
# - Season timing
# - Request priority
# - Department financial pressure
#
# KORBI gives decision support only.
# Final approval remains a human decision.
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

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


SIMULATION_DATE = "2027-10-01"


# ============================================================
# SPORT SEASON MAP
# ============================================================

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


# ============================================================
# PURCHASE REQUEST FIELDS
# ============================================================

REQUEST_FIELDS = [

    "request_id",
    "request_date",
    "program_code",
    "program_name",
    "expense_category",
    "requester",
    "vendor",
    "description",
    "business_justification",
    "priority",
    "amount",

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

    "financial_status",
    "department_forecast_percent",
    "department_uncommitted_reserve",

    "season",
    "forecast_confidence",
    "korbi_recommendation",
    "korbi_reason",
    "suggested_action",

    "status",
    "reviewed_by",
    "review_date",
    "decision_notes",
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


def money(value):

    return f"${value:,.0f}"


def percent(value):

    return f"{value:.1f}%"


def safe_float(value):

    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


# ============================================================
# LOAD PROGRAM BUDGETS
# ============================================================

def load_programs():

    rows = read_csv(
        BUDGET_FILE
    )

    if not rows:

        raise FileNotFoundError(
            f"No budget data found:\n{BUDGET_FILE}"
        )

    programs = {}

    for row in rows:

        code = row[
            "program_code"
        ]

        programs[code] = {

            "program_name":
                row["program_name"],

            "expense_category":
                row["expense_category"],

            "budget":
                safe_float(
                    row["category_budget"]
                ),

            "budget_status":
                row.get(
                    "budget_status",
                    ""
                ),

            "source":
                row.get(
                    "source",
                    ""
                ),
        }

    return programs


# ============================================================
# SELECT PROGRAM
# ============================================================

def choose_program(programs):

    codes = sorted(
        programs.keys(),
        key=lambda code:
            programs[code]["program_name"]
    )

    print()
    print("SELECT PROGRAM")
    print("==============")

    for number, code in enumerate(
        codes,
        start=1
    ):

        season = (
            SPORT_SEASONS.get(
                code,
                "UNKNOWN"
            )
        )

        print(
            f"{number}. "
            f"{programs[code]['program_name']} "
            f"({season})"
        )

    while True:

        value = input(
            "\nEnter program number: "
        ).strip()

        try:

            number = int(value)

            if (
                1
                <= number
                <= len(codes)
            ):

                return (
                    codes[number - 1]
                )

        except ValueError:
            pass

        print(
            "Enter one of the numbers shown."
        )


# ============================================================
# PRIORITY
# ============================================================

def choose_priority():

    print()
    print("REQUEST PRIORITY")
    print("================")

    print()
    print(
        "1. CRITICAL - Continuity / Safety"
    )

    print(
        "   Required to safely continue "
        "operations, competition, practice, "
        "or meet a legitimate compliance need."
    )

    print()
    print(
        "2. NECESSARY - Replacement / Preventive"
    )

    print(
        "   Needed to replace worn or unreliable "
        "equipment or prevent an operational issue."
    )

    print()
    print(
        "3. ENHANCEMENT - Upgrade / Wish List"
    )

    print(
        "   Improves performance, convenience, "
        "technology, or experience but current "
        "operations can continue without it."
    )

    while True:

        value = input(
            "\nEnter priority number (1-3): "
        ).strip()

        if value == "1":
            return "CRITICAL"

        if value == "2":
            return "NECESSARY"

        if value == "3":
            return "ENHANCEMENT"

        print(
            "Enter 1, 2, or 3."
        )


# ============================================================
# REQUEST AMOUNT
# ============================================================

def get_amount():

    while True:

        value = input(
            "Request amount: $"
        ).replace(
            ",",
            ""
        ).strip()

        try:

            amount = float(value)

            if amount > 0:
                return round(
                    amount,
                    2
                )

        except ValueError:
            pass

        print(
            "Enter an amount greater than zero."
        )


# ============================================================
# SPORT FINANCIAL POSITION
# ============================================================

def calculate_sport_position(
    program_code,
    annual_budget
):

    ledger = read_csv(
        LEDGER_FILE
    )

    future = read_csv(
        FUTURE_FILE
    )

    requests = read_csv(
        REQUEST_FILE
    )

    q1_actuals = sum(

        safe_float(row["amount"])

        for row in ledger

        if (
            row.get(
                "program_code"
            ) == program_code

            and row.get(
                "transaction_type"
            ) == "ACTUAL"

            and row.get(
                "status"
            ) == "PAID"
        )
    )

    open_pos = sum(

        safe_float(row["amount"])

        for row in ledger

        if (
            row.get(
                "program_code"
            ) == program_code

            and row.get(
                "transaction_type"
            ) == "PO"

            and row.get(
                "status"
            ) == "OPEN"
        )
    )

    scheduled_future = sum(

        safe_float(row["amount"])

        for row in future

        if (
            row.get(
                "program_code"
            ) == program_code

            and row.get(
                "status"
            ) == "PLANNED"

            and row.get(
                "confidence"
            ) == "HIGH"
        )
    )

    expected_future = sum(

        safe_float(row["amount"])

        for row in future

        if (
            row.get(
                "program_code"
            ) == program_code

            and row.get(
                "status"
            ) == "PLANNED"

            and row.get(
                "confidence"
            ) in {
                "MEDIUM",
                "LOW",
            }
        )
    )

    existing_pending = sum(

        safe_float(row["amount"])

        for row in requests

        if (
            row.get(
                "program_code"
            ) == program_code

            and row.get(
                "status"
            ) == "PENDING"
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

        "q1_actuals":
            q1_actuals,

        "open_pos":
            open_pos,

        "scheduled_future":
            scheduled_future,

        "expected_future":
            expected_future,

        "existing_pending":
            existing_pending,

        "baseline_projected":
            baseline_projected,

        "baseline_remaining":
            baseline_remaining,

        "baseline_percent":
            baseline_percent,
    }


# ============================================================
# DEPARTMENT POSITION
# ============================================================

def get_department_position():

    rows = read_csv(
        DEPARTMENT_FILE
    )

    if not rows:

        return {
            "annual_budget": 0,
            "projected": 0,
            "reserve": 0,
            "forecast_percent": 0,
        }

    annual = sum(
        safe_float(
            row["annual_budget"]
        )
        for row in rows
    )

    projected = sum(
        safe_float(
            row["projected_year_end"]
        )
        for row in rows
    )

    reserve = sum(
        safe_float(
            row["uncommitted_reserve"]
        )
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

        "annual_budget":
            annual,

        "projected":
            projected,

        "reserve":
            reserve,

        "forecast_percent":
            forecast_percent,
    }


# ============================================================
# FINANCIAL STATUS
# ============================================================

def classify_financial_status(
    projected_percent
):

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
# FORECAST CONFIDENCE
# ============================================================

def forecast_confidence(
    scheduled,
    expected
):

    total_future = (
        scheduled
        + expected
    )

    if total_future <= 0:
        return "LOW"

    if scheduled <= 0:
        return "MEDIUM"

    high_share = (
        scheduled
        / total_future
    )

    if high_share >= 0.60:
        return "HIGH"

    return "MEDIUM"


# ============================================================
# KORBI RECOMMENDATION
# ============================================================

def build_recommendation(
    priority,
    season,
    baseline_percent,
    projected_percent,
    remaining_after,
    request_amount,
    department_forecast,
    department_reserve
):

    status = classify_financial_status(
        projected_percent
    )

    # --------------------------------------------------------
    # HARD OVERRUN
    # --------------------------------------------------------

    if projected_percent > 100:

        if priority == "CRITICAL":

            return (
                "ESCALATE - CRITICAL NEED",

                (
                    "The request would push the program "
                    "over its projected annual operating "
                    "budget. Because the request is "
                    "classified as critical, it should "
                    "be escalated rather than automatically "
                    "denied."
                ),

                (
                    "Identify a funding source, transfer, "
                    "offsetting savings, or senior approval "
                    "before committing funds."
                ),
            )

        return (
            "DENY / DEFER",

            (
                "The request would push projected "
                "year-end spending above the program's "
                "annual operating allocation."
            ),

            (
                "Defer the purchase or identify documented "
                "offsetting savings before reconsideration."
            ),
        )

    # --------------------------------------------------------
    # 95-100%
    # --------------------------------------------------------

    if projected_percent >= 95:

        if priority == "CRITICAL":

            return (
                "ESCALATE FOR APPROVAL",

                (
                    "The request appears operationally "
                    "critical but would leave the program "
                    "with very little year-end flexibility."
                ),

                (
                    "Require management approval and verify "
                    "remaining seasonal obligations before "
                    "issuing the purchase."
                ),
            )

        if priority == "NECESSARY":

            return (
                "HOLD FOR REVIEW",

                (
                    "The request may be necessary, but the "
                    "program is projected to use at least "
                    "95% of its annual operating budget."
                ),

                (
                    "Confirm remaining travel and operating "
                    "requirements and look for an offset "
                    "before approval."
                ),
            )

        return (
            "DEFER",

            (
                "The request is an enhancement and the "
                "program is already projected to operate "
                "with minimal remaining budget capacity."
            ),

            (
                "Reconsider later in the year if projected "
                "savings become available."
            ),
        )

    # --------------------------------------------------------
    # 90-95%
    # --------------------------------------------------------

    if projected_percent >= 90:

        if priority == "CRITICAL":

            return (
                "APPROVE WITH MANAGEMENT REVIEW",

                (
                    "The request addresses a critical need "
                    "and remains within budget, but projected "
                    "year-end utilization would enter the "
                    "caution range."
                ),

                (
                    "Approve only after confirming no higher "
                    "priority seasonal obligation is at risk."
                ),
            )

        if priority == "NECESSARY":

            return (
                "HOLD FOR REVIEW",

                (
                    "The request remains within budget but "
                    "would leave limited flexibility for "
                    "unplanned expenses."
                ),

                (
                    "Verify the need and remaining season "
                    "forecast before committing funds."
                ),
            )

        return (
            "DEFER",

            (
                "The purchase is an enhancement and the "
                "program would be projected above 90% of "
                "its operating budget."
            ),

            (
                "Preserve the remaining cushion for travel, "
                "competition, equipment replacement, and "
                "unexpected costs."
            ),
        )

    # --------------------------------------------------------
    # 80-90%
    # --------------------------------------------------------

    if projected_percent >= 80:

        if priority == "CRITICAL":

            return (
                "APPROVE",

                (
                    "The request addresses a critical need "
                    "and the program retains a reasonable "
                    "forecasted budget cushion."
                ),

                (
                    "Proceed through normal purchasing "
                    "controls."
                ),
            )

        if priority == "NECESSARY":

            return (
                "APPROVE WITH CAUTION",

                (
                    "The request appears operationally "
                    "necessary and remains within forecasted "
                    "budget capacity."
                ),

                (
                    "Proceed, but continue monitoring "
                    "remaining seasonal expenses."
                ),
            )

        return (
            "CONSIDER IF FUNDS REMAIN",

            (
                "The enhancement currently fits within the "
                "forecast, but the program is already in the "
                "monitor range."
            ),

            (
                "Compare the benefit of the purchase against "
                "the value of preserving year-end flexibility."
            ),
        )

    # --------------------------------------------------------
    # BELOW 80%
    # --------------------------------------------------------

    if priority == "CRITICAL":

        recommendation = (
            "APPROVE"
        )

        reason = (
            "The request addresses a critical need and "
            "the current forecast shows adequate capacity."
        )

        action = (
            "Proceed through normal purchasing controls."
        )

    elif priority == "NECESSARY":

        recommendation = (
            "APPROVE"
        )

        reason = (
            "The request appears necessary and the program "
            "retains a healthy projected financial cushion."
        )

        action = (
            "Proceed if the business justification and "
            "purchase documentation are valid."
        )

    else:

        recommendation = (
            "CONSIDER"
        )

        reason = (
            "The request is an enhancement, but current "
            "forecasted spending leaves sufficient budget "
            "capacity for consideration."
        )

        action = (
            "Evaluate strategic value, timing, and alternative "
            "uses of the remaining budget before approval."
        )

    # --------------------------------------------------------
    # DEPARTMENT PRESSURE MODIFIER
    # --------------------------------------------------------

    if (
        priority == "ENHANCEMENT"
        and department_forecast >= 96
        and recommendation == "CONSIDER"
    ):

        recommendation = (
            "CONSIDER WITH CAUTION"
        )

        reason += (
            " Department-wide spending is also projected "
            "near the annual plan, reducing overall "
            "financial flexibility."
        )

        action = (
            "Confirm the purchase creates sufficient value "
            "to justify using limited department reserve."
        )

    return (
        recommendation,
        reason,
        action,
    )


# ============================================================
# REQUEST ID
# ============================================================

def generate_request_id():

    rows = read_csv(
        REQUEST_FILE
    )

    prefix = (
        "PR-20271001-"
    )

    highest = 0

    for row in rows:

        request_id = row.get(
            "request_id",
            ""
        )

        if not request_id.startswith(
            prefix
        ):
            continue

        try:

            number = int(
                request_id.split(
                    "-"
                )[-1]
            )

            highest = max(
                highest,
                number
            )

        except ValueError:
            pass

    return (
        f"{prefix}"
        f"{highest + 1:03d}"
    )


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

def display_analysis(
    request
):

    print()
    print("KORBI FINANCIAL ASSESSMENT")
    print("==========================")

    print()
    print(
        f"Program:                 "
        f"{request['program_name']}"
    )

    print(
        f"Season:                  "
        f"{request['season']}"
    )

    print(
        f"Request Amount:          "
        f"{money(request['amount'])}"
    )

    print(
        f"Priority:                "
        f"{request['priority']}"
    )

    print()
    print("CURRENT PROGRAM POSITION")
    print("------------------------")

    print(
        f"Annual Operating Budget: "
        f"{money(request['annual_budget'])}"
    )

    print(
        f"Q1 Actual Spend:         "
        f"{money(request['q1_actuals'])}"
    )

    print(
        f"Open POs:                "
        f"{money(request['open_pos'])}"
    )

    print(
        f"Scheduled Future Spend:  "
        f"{money(request['scheduled_future'])}"
    )

    print(
        f"Expected Future Spend:   "
        f"{money(request['expected_future'])}"
    )

    print(
        f"Pending Requests:        "
        f"{money(request['existing_pending_requests'])}"
    )

    print()
    print("FORECAST BEFORE REQUEST")
    print("-----------------------")

    print(
        f"Projected Year-End:      "
        f"{money(request['baseline_projected'])}"
    )

    print(
        f"Projected Remaining:     "
        f"{money(request['baseline_remaining'])}"
    )

    print(
        f"Projected Budget Used:   "
        f"{percent(request['baseline_percent'])}"
    )

    print()
    print("FORECAST WITH REQUEST")
    print("---------------------")

    print(
        f"Projected Year-End:      "
        f"{money(request['projected_with_request'])}"
    )

    print(
        f"Projected Remaining:     "
        f"{money(request['remaining_with_request'])}"
    )

    print(
        f"Projected Budget Used:   "
        f"{percent(request['percent_with_request'])}"
    )

    print(
        f"Financial Status:        "
        f"{request['financial_status']}"
    )

    print(
        f"Forecast Confidence:     "
        f"{request['forecast_confidence']}"
    )

    print()
    print("DEPARTMENT CONTEXT")
    print("------------------")

    print(
        f"Department Forecast:     "
        f"{percent(request['department_forecast_percent'])}"
    )

    print(
        f"Department Reserve:      "
        f"{money(request['department_uncommitted_reserve'])}"
    )

    print()
    print("KORBI RECOMMENDATION")
    print("--------------------")

    print(
        request[
            "korbi_recommendation"
        ]
    )

    print()
    print("Assessment:")

    print(
        request[
            "korbi_reason"
        ]
    )

    print()
    print("Suggested Action:")

    print(
        request[
            "suggested_action"
        ]
    )


# ============================================================
# SAVE REQUEST
# ============================================================

def save_request(
    request
):

    file_exists = (
        REQUEST_FILE.exists()
    )

    with open(
        REQUEST_FILE,
        "a",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=REQUEST_FIELDS
        )

        if not file_exists:

            writer.writeheader()

        writer.writerow(
            request
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
        "PURCHASE REQUEST / "
        "FINANCIAL RECOMMENDATION"
    )

    print()
    print(
        "Financial Position: "
        "October 1, 2027"
    )

    programs = load_programs()

    code = choose_program(
        programs
    )

    program = programs[code]

    requester = input(
        "\nRequester name: "
    ).strip()

    vendor = input(
        "Vendor: "
    ).strip()

    description = input(
        "Purchase description: "
    ).strip()

    justification = input(
        "Business justification: "
    ).strip()

    priority = choose_priority()

    amount = get_amount()

    position = (
        calculate_sport_position(
            code,
            program["budget"]
        )
    )

    department = (
        get_department_position()
    )

    projected_with_request = (
        position[
            "baseline_projected"
        ]
        + amount
    )

    remaining_with_request = (
        program["budget"]
        - projected_with_request
    )

    percent_with_request = (
        projected_with_request
        / program["budget"]
        * 100
        if program["budget"]
        else 0
    )

    status = (
        classify_financial_status(
            percent_with_request
        )
    )

    confidence = (
        forecast_confidence(
            position[
                "scheduled_future"
            ],
            position[
                "expected_future"
            ]
        )
    )

    (
        recommendation,
        reason,
        suggested_action
    ) = build_recommendation(

        priority,

        SPORT_SEASONS.get(
            code,
            "UNKNOWN"
        ),

        position[
            "baseline_percent"
        ],

        percent_with_request,

        remaining_with_request,

        amount,

        department[
            "forecast_percent"
        ],

        department[
            "reserve"
        ],
    )

    request = {

        "request_id":
            generate_request_id(),

        "request_date":
            SIMULATION_DATE,

        "program_code":
            code,

        "program_name":
            program[
                "program_name"
            ],

        "expense_category":
            program[
                "expense_category"
            ],

        "requester":
            requester,

        "vendor":
            vendor,

        "description":
            description,

        "business_justification":
            justification,

        "priority":
            priority,

        "amount":
            amount,

        "annual_budget":
            program["budget"],

        "q1_actuals":
            position[
                "q1_actuals"
            ],

        "open_pos":
            position[
                "open_pos"
            ],

        "scheduled_future":
            position[
                "scheduled_future"
            ],

        "expected_future":
            position[
                "expected_future"
            ],

        "existing_pending_requests":
            position[
                "existing_pending"
            ],

        "baseline_projected":
            position[
                "baseline_projected"
            ],

        "baseline_remaining":
            position[
                "baseline_remaining"
            ],

        "baseline_percent":
            position[
                "baseline_percent"
            ],

        "projected_with_request":
            projected_with_request,

        "remaining_with_request":
            remaining_with_request,

        "percent_with_request":
            percent_with_request,

        "financial_status":
            status,

        "department_forecast_percent":
            department[
                "forecast_percent"
            ],

        "department_uncommitted_reserve":
            department[
                "reserve"
            ],

        "season":
            SPORT_SEASONS.get(
                code,
                "UNKNOWN"
            ),

        "forecast_confidence":
            confidence,

        "korbi_recommendation":
            recommendation,

        "korbi_reason":
            reason,

        "suggested_action":
            suggested_action,

        "status":
            "PENDING",

        "reviewed_by":
            "",

        "review_date":
            "",

        "decision_notes":
            "",
    }

    display_analysis(
        request
    )

    print()
    print("REQUEST DETAILS")
    print("---------------")

    print(
        f"Request ID:              "
        f"{request['request_id']}"
    )

    print(
        f"Requester:               "
        f"{requester}"
    )

    print(
        f"Vendor:                  "
        f"{vendor}"
    )

    print(
        f"Description:             "
        f"{description}"
    )

    print(
        f"Business Justification:  "
        f"{justification}"
    )

    while True:

        answer = input(
            "\nSave purchase request? (Y/N): "
        ).strip().upper()

        if answer == "Y":

            save_request(
                request
            )

            print()
            print("REQUEST SAVED")
            print("=============")

            print(
                f"Request ID:           "
                f"{request['request_id']}"
            )

            print(
                f"Status:               "
                f"{request['status']}"
            )

            print(
                f"KORBI Recommendation: "
                f"{request['korbi_recommendation']}"
            )

            break

        if answer == "N":

            print()
            print("REQUEST NOT SAVED")
            print("=================")

            break

        print(
            "Enter Y or N."
        )


if __name__ == "__main__":

    try:

        run()

    except Exception as error:

        print()
        print("KORBI PURCHASE REQUEST ERROR")
        print("============================")
        print(error)