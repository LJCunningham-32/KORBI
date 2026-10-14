import requests
from bs4 import BeautifulSoup

url = "https://www.gvsu.edu/about.htm"

response = requests.get(url)

print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://www.gvsu.edu/about.htm"

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Remove webpage elements we don't want
for tag in soup(["script", "style", "nav", "footer"]):
    tag.decompose()

# Extract readable text
page_text = soup.get_text(separator="\n", strip=True)

# Build the information we want to save
output = f"""
SCHOOL: Grand Valley State University
SOURCE: {url}
DATE COLLECTED: {datetime.now().strftime("%Y-%m-%d")}

------------------------------
SCRAPED WEBPAGE CONTENT
------------------------------

{page_text}
"""

# Save everything into a text file
with open("gvsu_about.txt", "w", encoding="utf-8") as file:
    file.write(output)

print("GVSU page scraped successfully.")
print("Saved to: gvsu_about.txt")