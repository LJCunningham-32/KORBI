import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

DOCUMENT_FOLDER = (
    PROJECT_FOLDER
    / "Data"
    / "Raw"
    / "Research"
    / "Documents"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "research_document_hits.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# DOCUMENT PRIORITY RULES
# --------------------------------------------------

HIGH_PRIORITY_FILE_TERMS = [
    "SSU",
    "SONOMA",
    "ATHLETICS",
    "BUDGET",
    "COMMITMENT",
]

MEDIUM_PRIORITY_FILE_TERMS = [
    "CSU",
    "CALSTATE",
]

LOW_PRIORITY_FILE_TERMS = [
    "IPEDS",
    "COLLEGE_SCORECARD",
    "NCAA",
]


# --------------------------------------------------
# SEARCH TERMS
# --------------------------------------------------

SEARCH_TERMS = [
    "salary",
    "salaries",
    "benefits",
    "personnel",
    "administration",
    "administrative",
    "staff",
    "coach",
    "coaches",
    "facilities",
    "facility",
    "maintenance",
    "sports medicine",
    "athletic training",
    "compliance",
    "insurance",
    "travel",
    "equipment",
    "scholarship",
    "scholarships",
    "student aid",
    "recruiting",
    "ticket",
    "tickets",
    "fundraising",
    "donation",
    "donations",
    "sponsorship",
    "sponsorships",
    "operating fund",
    "institutional support",
    "general fund",
    "student fee",
    "student fees",
    "ira",
    "instructionally related activities",
    "budget",
    "expense",
    "expenses",
    "revenue",
    "revenues",
]


# --------------------------------------------------
# HIGH-VALUE TERMS
# --------------------------------------------------

HIGH_VALUE_TERMS = {
    "salary",
    "salaries",
    "benefits",
    "personnel",
    "administration",
    "administrative",
    "facilities",
    "facility",
    "maintenance",
    "sports medicine",
    "athletic training",
    "compliance",
    "insurance",
    "institutional support",
    "general fund",
    "student fee",
    "student fees",
    "ira",
    "instructionally related activities",
}


# --------------------------------------------------
# STRONG FINANCIAL PHRASES
# --------------------------------------------------

STRONG_FINANCIAL_PHRASES = [
    "total expenses",
    "total expense",
    "total revenue",
    "total revenues",
    "cost/sa",
    "cost per student",
    "cost per student-athlete",
    "annual salary",
    "per year",
    "/yr",
    "allocation",
    "funding sources",
    "operating fund allocation",
    "budget savings",
    "projected savings",
    "one-time funding",
    "appropriation",
    "fte",
]


# --------------------------------------------------
# WEAK / BOILERPLATE PHRASES
# --------------------------------------------------

WEAK_PHRASES = [
    "table of contents",
    "chapter",
    "recommendation",
    "recommendations",
]


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


# --------------------------------------------------
# DOCUMENT PRIORITY
# --------------------------------------------------

def get_document_priority(file_name):

    upper_name = file_name.upper()

    for term in HIGH_PRIORITY_FILE_TERMS:

        if term in upper_name:
            return "HIGH"

    for term in MEDIUM_PRIORITY_FILE_TERMS:

        if term in upper_name:
            return "MEDIUM"

    for term in LOW_PRIORITY_FILE_TERMS:

        if term in upper_name:
            return "LOW"

    return "MEDIUM"


# --------------------------------------------------
# READ HTML
# --------------------------------------------------

def read_html(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        html = file.read()

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup(
        ["script", "style", "nav", "footer"]
    ):
        tag.decompose()

    return clean_text(
        soup.get_text(" ")
    )


# --------------------------------------------------
# READ TEXT
# --------------------------------------------------

def read_text(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as file:

        return clean_text(
            file.read()
        )


# --------------------------------------------------
# READ CSV
# --------------------------------------------------

def read_csv(file_path):

    pieces = []

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        errors="replace",
        newline=""
    ) as file:

        reader = csv.reader(file)

        for row in reader:

            pieces.append(
                " | ".join(row)
            )

    return clean_text(
        " ".join(pieces)
    )


# --------------------------------------------------
# READ PDF
# --------------------------------------------------

def read_pdf(file_path):

    try:

        from pypdf import PdfReader

    except ImportError:

        print(
            "ERROR: pypdf is not installed."
        )

        print(
            "Run: python -m pip install pypdf"
        )

        return ""

    try:

        reader = PdfReader(
            str(file_path)
        )

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text()

            if text:

                pages.append(
                    f"[PAGE {page_number}] {text}"
                )

        return clean_text(
            " ".join(pages)
        )

    except Exception as error:

        print(
            f"FAILED TO READ PDF: "
            f"{file_path.name}"
        )

        print(
            f"Reason: {error}"
        )

        return ""


# --------------------------------------------------
# READ DOCUMENT
# --------------------------------------------------

def read_document(file_path):

    extension = (
        file_path.suffix
        .lower()
    )

    if extension == ".html":
        return read_html(file_path)

    if extension == ".txt":
        return read_text(file_path)

    if extension == ".csv":
        return read_csv(file_path)

    if extension == ".pdf":
        return read_pdf(file_path)

    return ""


# --------------------------------------------------
# FIND PAGE NUMBER
# --------------------------------------------------

def find_page_number(text, position):

    text_before_hit = text[:position]

    matches = list(
        re.finditer(
            r"\[PAGE (\d+)\]",
            text_before_hit
        )
    )

    if not matches:
        return ""

    return matches[-1].group(1)


# --------------------------------------------------
# DETECT DOLLAR AMOUNTS
# --------------------------------------------------

def find_dollar_amounts(context):

    pattern = (
        r"\$"
        r"\s*"
        r"\d{1,3}"
        r"(?:,\d{3})*"
        r"(?:\.\d+)?"
        r"(?:\s*[KkMm])?"
    )

    return re.findall(
        pattern,
        context
    )


# --------------------------------------------------
# DETECT PERCENTAGES
# --------------------------------------------------

def find_percentages(context):

    return re.findall(
        r"\b\d+(?:\.\d+)?\s*%",
        context
    )


# --------------------------------------------------
# DETECT FTE
# --------------------------------------------------

def has_fte(context):

    return bool(
        re.search(
            r"\bFTE\b",
            context,
            re.IGNORECASE
        )
    )


# --------------------------------------------------
# DETECT STRONG FINANCIAL PHRASES
# --------------------------------------------------

def find_strong_phrases(context):

    lower_context = context.lower()

    matches = []

    for phrase in STRONG_FINANCIAL_PHRASES:

        if phrase in lower_context:
            matches.append(phrase)

    return matches


# --------------------------------------------------
# DETECT WEAK PHRASES
# --------------------------------------------------

def find_weak_phrases(context):

    lower_context = context.lower()

    matches = []

    for phrase in WEAK_PHRASES:

        if phrase in lower_context:
            matches.append(phrase)

    return matches


# --------------------------------------------------
# FINANCIAL EVIDENCE SCORE
# --------------------------------------------------

def calculate_financial_evidence(context):

    score = 0

    dollar_amounts = find_dollar_amounts(
        context
    )

    percentages = find_percentages(
        context
    )

    strong_phrases = find_strong_phrases(
        context
    )

    weak_phrases = find_weak_phrases(
        context
    )

    fte_present = has_fte(
        context
    )

    # ----------------------------------------------
    # DOLLAR VALUES
    # ----------------------------------------------

    if dollar_amounts:
        score += 3

    if len(dollar_amounts) >= 3:
        score += 1

    # ----------------------------------------------
    # FINANCIAL LANGUAGE
    # ----------------------------------------------

    if strong_phrases:
        score += 2

    if len(strong_phrases) >= 2:
        score += 1

    # ----------------------------------------------
    # FTE / STAFF STRUCTURE
    # ----------------------------------------------

    if fte_present:
        score += 1

    # ----------------------------------------------
    # PERCENTAGE DATA
    # ----------------------------------------------

    if percentages:
        score += 1

    # ----------------------------------------------
    # PENALTY FOR BOILERPLATE
    # ----------------------------------------------

    if weak_phrases:
        score -= 1

    score = max(
        0,
        score
    )

    if score >= 5:
        evidence_type = "QUANTIFIED"

    elif score >= 2:
        evidence_type = "SUPPORTING"

    else:
        evidence_type = "NARRATIVE"

    return {
        "score": score,
        "evidence_type": evidence_type,
        "dollar_amounts": dollar_amounts,
        "percentages": percentages,
        "fte_present": fte_present,
        "strong_phrases": strong_phrases,
    }


# --------------------------------------------------
# FIND HITS
# --------------------------------------------------

def find_hits(
    source_file,
    text
):

    hits = []

    lower_text = text.lower()

    document_priority = (
        get_document_priority(
            source_file.name
        )
    )

    for term in SEARCH_TERMS:

        term_lower = term.lower()

        start = 0

        while True:

            position = lower_text.find(
                term_lower,
                start
            )

            if position == -1:
                break

            context_start = max(
                0,
                position - 400
            )

            context_end = min(
                len(text),
                position
                + len(term)
                + 650
            )

            context = clean_text(
                text[
                    context_start:
                    context_end
                ]
            )

            page_number = find_page_number(
                text,
                position
            )

            if term in HIGH_VALUE_TERMS:
                term_priority = "HIGH"
            else:
                term_priority = "NORMAL"

            base_score = 0

            if document_priority == "HIGH":
                base_score += 3

            elif document_priority == "MEDIUM":
                base_score += 2

            else:
                base_score += 1

            if term_priority == "HIGH":
                base_score += 2
            else:
                base_score += 1

            context_lower = context.lower()

            if (
                "sonoma state" in context_lower
                or "athletics" in context_lower
            ):
                base_score += 2

            evidence = (
                calculate_financial_evidence(
                    context
                )
            )

            total_score = (
                base_score
                + evidence["score"]
            )

            hits.append({

                "total_score":
                    total_score,

                "base_priority_score":
                    base_score,

                "financial_evidence_score":
                    evidence["score"],

                "evidence_type":
                    evidence["evidence_type"],

                "document_priority":
                    document_priority,

                "term_priority":
                    term_priority,

                "source_file":
                    source_file.name,

                "page_number":
                    page_number,

                "search_term":
                    term,

                "has_dollar_amount":
                    "YES"
                    if evidence["dollar_amounts"]
                    else "NO",

                "dollar_amounts":
                    " | ".join(
                        evidence["dollar_amounts"]
                    ),

                "has_percentage":
                    "YES"
                    if evidence["percentages"]
                    else "NO",

                "percentages":
                    " | ".join(
                        evidence["percentages"]
                    ),

                "has_fte":
                    "YES"
                    if evidence["fte_present"]
                    else "NO",

                "strong_financial_phrases":
                    " | ".join(
                        evidence["strong_phrases"]
                    ),

                "context":
                    context,

                "review_status":
                    "UNREVIEWED",

                "financial_relevance":
                    "",

                "cost_category":
                    "",

                "verified_amount":
                    "",

                "notes":
                    "",
            })

            start = (
                position
                + len(term)
            )

    return hits


# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

def remove_duplicates(hits):

    unique = []

    seen = set()

    for hit in hits:

        key = (
            hit["source_file"],
            hit["page_number"],
            hit["context"][:500].lower()
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(hit)

    return unique


# --------------------------------------------------
# SORT HITS
# --------------------------------------------------

def sort_hits(hits):

    return sorted(
        hits,
        key=lambda hit: (
            -hit["total_score"],
            -hit["financial_evidence_score"],
            hit["source_file"],
            hit["page_number"],
        )
    )


# --------------------------------------------------
# PROCESS DOCUMENTS
# --------------------------------------------------

def process_documents():

    if not DOCUMENT_FOLDER.exists():

        print(
            "ERROR: Documents folder does not exist."
        )

        return []

    files = [
        path
        for path
        in DOCUMENT_FOLDER.iterdir()
        if path.is_file()
    ]

    if not files:

        print(
            "No documents found."
        )

        return []

    all_hits = []

    print()
    print(
        "QUANTIFIED FINANCIAL EVIDENCE EXTRACTION"
    )

    print(
        "========================================"
    )

    for file_path in files:

        priority = get_document_priority(
            file_path.name
        )

        print()
        print(
            f"READING: {file_path.name}"
        )

        print(
            f"  Document Priority: {priority}"
        )

        text = read_document(
            file_path
        )

        if not text:

            print(
                "  No readable text extracted."
            )

            continue

        hits = find_hits(
            file_path,
            text
        )

        print(
            f"  Raw hits: {len(hits):,}"
        )

        all_hits.extend(
            hits
        )

    return sort_hits(
        remove_duplicates(
            all_hits
        )
    )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

def save_hits(hits):

    fieldnames = [
        "total_score",
        "base_priority_score",
        "financial_evidence_score",
        "evidence_type",
        "document_priority",
        "term_priority",
        "source_file",
        "page_number",
        "search_term",
        "has_dollar_amount",
        "dollar_amounts",
        "has_percentage",
        "percentages",
        "has_fte",
        "strong_financial_phrases",
        "context",
        "review_status",
        "financial_relevance",
        "cost_category",
        "verified_amount",
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

        writer.writerows(
            hits
        )


# --------------------------------------------------
# SHOW BEST QUANTIFIED HITS
# --------------------------------------------------

def show_best_hits(hits):

    quantified = [
        hit
        for hit in hits
        if hit["evidence_type"]
        == "QUANTIFIED"
    ]

    print()
    print(
        "TOP QUANTIFIED FINANCIAL HITS"
    )

    print(
        "============================="
    )

    for hit in quantified[:15]:

        print()
        print(
            f"TOTAL SCORE: "
            f"{hit['total_score']}"
        )

        print(
            f"EVIDENCE SCORE: "
            f"{hit['financial_evidence_score']}"
        )

        print(
            f"FILE: "
            f"{hit['source_file']}"
        )

        if hit["page_number"]:

            print(
                f"PAGE: "
                f"{hit['page_number']}"
            )

        print(
            f"TERM: "
            f"{hit['search_term']}"
        )

        print(
            f"DOLLAR AMOUNTS: "
            f"{hit['dollar_amounts']}"
        )

        print(
            f"FTE: "
            f"{hit['has_fte']}"
        )

        print(
            "CONTEXT:"
        )

        print(
            hit["context"]
        )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def show_summary(hits):

    quantified = sum(
        1
        for hit in hits
        if hit["evidence_type"]
        == "QUANTIFIED"
    )

    supporting = sum(
        1
        for hit in hits
        if hit["evidence_type"]
        == "SUPPORTING"
    )

    narrative = sum(
        1
        for hit in hits
        if hit["evidence_type"]
        == "NARRATIVE"
    )

    print()
    print(
        "EXTRACTION SUMMARY"
    )

    print(
        "=================="
    )

    print(
        f"Total Unique Hits: "
        f"{len(hits):,}"
    )

    print(
        f"Quantified Hits: "
        f"{quantified:,}"
    )

    print(
        f"Supporting Hits: "
        f"{supporting:,}"
    )

    print(
        f"Narrative Hits: "
        f"{narrative:,}"
    )

    print()
    print(
        f"Output:"
    )

    print(
        OUTPUT_FILE
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    hits = process_documents()

    save_hits(
        hits
    )

    show_summary(
        hits
    )

    show_best_hits(
        hits
    )


if __name__ == "__main__":
    main()