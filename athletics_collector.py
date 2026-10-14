import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import time

# --------------------------------------------------
# PROJECT LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

SCHOOLS_FILE = PROJECT_FOLDER / "schools.csv"
RAW_FOLDER = PROJECT_FOLDER / "Data" / "Raw"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/154 Safari/537.36 "
        "AI Athletics academic research project"
    )
}


# --------------------------------------------------
# LOAD SCHOOLS FROM schools.csv
# --------------------------------------------------

def load_schools():

    schools = []

    with open(SCHOOLS_FILE, "r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:
            schools.append(row)

    return schools


# --------------------------------------------------
# SCRAPE ONE SCHOOL
# --------------------------------------------------

def scrape_school(school):

    school_id = school["school_id"]
    school_name = school["school_name"]
    url = school["athletics_url"]

    print()
    print("----------------------------------------")
    print(f"Collecting: {school_name}")
    print(f"Group: {school['group']}")
    print(f"Website: {url}")
    print("----------------------------------------")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print("Status code:", response.status_code)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove webpage code that is usually not useful.
        for tag in soup([
            "script",
            "style",
            "noscript",
            "svg"
        ]):
            tag.decompose()

        page_text = soup.get_text(
            separator="\n",
            strip=True
        )

        output = f"""
SCHOOL ID: {school_id}
SCHOOL: {school_name}
STATE: {school["state"]}
GROUP: {school["group"]}
STATUS: {school["status"]}
DIVISION: {school["division"]}
CONFERENCE: {school["conference"]}
SOURCE URL: {url}
DATE COLLECTED: {datetime.now().strftime("%Y-%m-%d")}
HTTP STATUS: {response.status_code}

========================================
RAW ATHLETICS WEBSITE CONTENT
========================================

{page_text}
"""

        filename = f"{school_id}_athletics_raw.txt"

        file_path = RAW_FOLDER / filename

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(output)

        print(f"SUCCESS: Saved {filename}")

    except requests.RequestException as error:

        print(f"FAILED: {school_name}")
        print("Reason:", error)


# --------------------------------------------------
# RUN COLLECTOR
# --------------------------------------------------

print()
print("AI ATHLETICS DATA COLLECTOR")
print("===========================")

schools = load_schools()

print(f"Schools loaded from schools.csv: {len(schools)}")

for school in schools:

    scrape_school(school)

    # Small delay so we do not hammer websites.
    time.sleep(2)

print()
print("===========================")
print(f"COLLECTION COMPLETE: {len(schools)} schools attempted")
print("===========================")