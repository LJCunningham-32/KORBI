import csv
from datetime import date
from pathlib import Path


# ==================================================
# KORBI
# Knowledge & Operations Resource
# for Business Intelligence
#
# PURCHASE REQUEST APPROVAL WORKFLOW
#
# TEST MODE
# ==================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

PURCHASE_REQUEST_FILE = (
    PROCESSED_FOLDER / "korbi_purchase_requests.csv"
)

LEDGER_FILE = (
    PROCESSED_FOLDER / "korbi_operational_ledger.csv"
)


# ==================================================
# HELPERS
# ==================================================

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


def format_money(value):

    try:
        return f"${float(value):,.0f}"

    except (ValueError, TypeError):
        return "$0"


# ==================================================
# FIND PENDING REQUESTS
# ==================================================

def get_pending_requests(rows):

    return [
        row
        for row in rows
        if row.get("status") == "PENDING"
    ]


# ==================================================
# SELECT REQUEST
# ==================================================

def choose_request(pending_requests):

    print()
    print("PENDING PURCHASE REQUESTS")
    print("=========================")

    for number, row in enumerate(
        pending_requests,
        start=1
    ):

        print()

        print(
            f"{number}. "
            f"{row['request_id']}"
        )

        print(
            f"   Program:        "
            f"{row['program_name']}"
        )

        print(
            f"   Requester:      "
            f"{row['requester']}"
        )

        print(
            f"   Description:    "
            f"{row['description']}"
        )

        print(
            f"   Amount:         "
            f"{format_money(row['amount'])}"
        )

        print(
            f"   Priority:       "
            f"{row['priority']}"
        )

        print(
            f"   KORBI:          "
            f"{row['korbi_recommendation']}"
        )

    while True:

        selection = input(
            "\nSelect request number: "
        ).strip()

        try:

            number = int(selection)

            if (
                1 <= number
                <= len(pending_requests)
            ):

                return pending_requests[
                    number - 1
                ]

        except ValueError:
            pass

        print(
            "Invalid selection."
        )


# ==================================================
# DISPLAY FULL REQUEST
# ==================================================

def display_request(row):

    print()
    print("PURCHASE REQUEST REVIEW")
    print("=======================")

    print(
        f"Request ID:              "
        f"{row['request_id']}"
    )

    print(
        f"Date:                    "
        f"{row['request_date']}"
    )

    print(
        f"Program:                 "
        f"{row['program_name']}"
    )

    print(
        f"Requester:               "
        f"{row['requester']}"
    )

    print(
        f"Vendor:                  "
        f"{row['vendor']}"
    )

    print(
        f"Description:             "
        f"{row['description']}"
    )

    print(
        f"Justification:           "
        f"{row['justification']}"
    )

    print(
        f"Priority:                "
        f"{row['priority']}"
    )

    print(
        f"Priority Type:           "
        f"{row['priority_reason']}"
    )

    print(
        f"Amount:                  "
        f"{format_money(row['amount'])}"
    )

    print()

    print("KORBI ANALYSIS")
    print("--------------")

    print(
        f"Recommendation:          "
        f"{row['korbi_recommendation']}"
    )

    print(
        f"Projected Status:        "
        f"{row['projected_status']}"
    )

    print(
        f"Projected Year-End:      "
        f"{format_money(row['projected_year_end'])}"
    )

    print(
        f"Projected Remaining:     "
        f"{format_money(row['projected_remaining'])}"
    )

    print(
        f"Required Savings:        "
        f"{format_money(row['required_savings'])}"
    )

    print()

    print("DATA QUALITY")
    print("------------")

    print(
        f"Budget Data:             "
        f"{row['budget_data_status']}"
    )

    print(
        f"Forecast Data:           "
        f"{row['forecast_data_status']}"
    )

    if (
        row["forecast_data_status"]
        == "NO FORECAST DATA"
    ):

        print()
        print(
            "WARNING: No forecast exists for "
            "this program/category."
        )

        print(
            "KORBI cannot assume that future "
            "spending will be $0."
        )


# ==================================================
# MANAGEMENT DECISION
# ==================================================

def choose_decision():

    print()
    print("MANAGEMENT DECISION")
    print("===================")

    print()
    print("1. APPROVE")
    print(
        "   Authorize the request to proceed."
    )

    print()
    print("2. DENY")
    print(
        "   Reject the purchase request."
    )

    print()
    print("3. DEFER")
    print(
        "   Keep the request for future "
        "consideration."
    )

    print()
    print("4. ESCALATE")
    print(
        "   Send for higher-level budget or "
        "management action."
    )

    print()
    print("5. CANCEL")
    print(
        "   Exit without changing the request."
    )

    decisions = {
        "1": "APPROVED",
        "2": "DENIED",
        "3": "DEFERRED",
        "4": "ESCALATED",
        "5": "CANCEL",
    }

    while True:

        selection = input(
            "\nEnter decision number: "
        ).strip()

        if selection in decisions:

            return decisions[selection]

        print(
            "Invalid selection. Enter 1-5."
        )


# ==================================================
# CONFIRM MANAGEMENT ACTION
# ==================================================

def confirm_decision(decision):

    print()
    print("CONFIRM DECISION")
    print("================")

    print(
        f"New Status: {decision}"
    )

    while True:

        answer = input(
            "\nConfirm? (Y/N): "
        ).strip().upper()

        if answer == "Y":
            return True

        if answer == "N":
            return False

        print(
            "Enter Y or N."
        )


# ==================================================
# UPDATE PURCHASE REQUEST REGISTER
# ==================================================

def update_purchase_request(
    all_requests,
    request_id,
    decision,
    reviewer,
    decision_notes
):

    if not all_requests:
        return

    original_fields = list(
        all_requests[0].keys()
    )

    extra_fields = [
        "reviewed_by",
        "review_date",
        "decision_notes",
    ]

    fieldnames = (
        original_fields.copy()
    )

    for field in extra_fields:

        if field not in fieldnames:

            fieldnames.append(field)

    for row in all_requests:

        if row["request_id"] == request_id:

            row["status"] = decision

            row["reviewed_by"] = (
                reviewer
            )

            row["review_date"] = (
                date.today().isoformat()
            )

            row["decision_notes"] = (
                decision_notes
            )

    write_csv(
        PURCHASE_REQUEST_FILE,
        all_requests,
        fieldnames
    )


# ==================================================
# UPDATE OPERATIONAL LEDGER
# ==================================================

def update_ledger(
    request_id,
    decision
):

    ledger = read_csv(
        LEDGER_FILE
    )

    if not ledger:
        return

    fieldnames = list(
        ledger[0].keys()
    )

    found = False

    for row in ledger:

        if (
            row["transaction_id"]
            == request_id
        ):

            row["status"] = decision
            found = True

    if not found:

        print()
        print(
            "WARNING: Matching ledger "
            "transaction was not found."
        )

        return

    write_csv(
        LEDGER_FILE,
        ledger,
        fieldnames
    )


# ==================================================
# PROCESS DECISION
# ==================================================

def process_decision(
    all_requests,
    selected_request
):

    display_request(
        selected_request
    )

    decision = choose_decision()

    if decision == "CANCEL":

        print()
        print(
            "No changes were made."
        )

        return

    reviewer = input(
        "\nReviewed by: "
    ).strip()

    decision_notes = input(
        "Decision notes: "
    ).strip()

    if not confirm_decision(
        decision
    ):

        print()
        print(
            "Decision cancelled. "
            "No changes were made."
        )

        return

    request_id = (
        selected_request["request_id"]
    )

    update_purchase_request(
        all_requests,
        request_id,
        decision,
        reviewer,
        decision_notes
    )

    update_ledger(
        request_id,
        decision
    )

    print()
    print("REQUEST UPDATED")
    print("===============")

    print(
        f"Request ID:     "
        f"{request_id}"
    )

    print(
        f"New Status:     "
        f"{decision}"
    )

    print(
        f"Reviewed By:    "
        f"{reviewer}"
    )

    print()

    if decision == "APPROVED":

        print(
            "The request is approved, but it "
            "has NOT yet been converted to a PO."
        )

    elif decision == "DENIED":

        print(
            "The request has been denied and "
            "will no longer count as a pending "
            "budget request."
        )

    elif decision == "DEFERRED":

        print(
            "The request has been deferred for "
            "future consideration."
        )

    elif decision == "ESCALATED":

        print(
            "The request has been escalated for "
            "additional management or budget action."
        )


# ==================================================
# MAIN WORKFLOW
# ==================================================

def run_approval_workflow():

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()

    print("PURCHASE APPROVAL WORKFLOW")
    print("==========================")

    print()

    print(
        "TEST MODE - No real Sonoma State "
        "financial transactions are being processed."
    )

    all_requests = read_csv(
        PURCHASE_REQUEST_FILE
    )

    pending_requests = (
        get_pending_requests(
            all_requests
        )
    )

    if not pending_requests:

        print()
        print(
            "No pending purchase requests "
            "were found."
        )

        return

    selected_request = (
        choose_request(
            pending_requests
        )
    )

    process_decision(
        all_requests,
        selected_request
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    try:

        run_approval_workflow()

    except Exception as error:

        print()
        print("KORBI APPROVAL WORKFLOW ERROR")
        print("=============================")
        print(error)