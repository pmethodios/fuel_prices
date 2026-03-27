import re
import os
import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# -----------------------------
# Constants
# -----------------------------
PAGE_URL = "https://www.fuelprices.gr/deltia_d.view"
BASE_URL = "https://www.fuelprices.gr/"
DOWNLOAD_FOLDER = "pdf_files"

# -----------------------------
# Extract date from PDF filename
# -----------------------------
def extract_date(url: str):
    """Extract datetime object from filenames like 25_03_2026"""
    match = re.search(r'(\d{2})_(\d{2})_(\d{4})', url)
    if match:
        day, month, year = match.groups()
        return datetime(int(year), int(month), int(day))
    return None

# -----------------------------
# Get latest PDF URL
# -----------------------------
def get_latest_pdf():
    response = requests.get(PAGE_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" in href:
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)

    if not pdf_links:
        raise Exception("No PDF links found")

    dated_links = [(url, extract_date(url)) for url in pdf_links if extract_date(url)]
    if not dated_links:
        raise Exception("No dated PDFs found")

    dated_links.sort(key=lambda x: x[1], reverse=True)

    print("Top 5 PDF candidates:")
    for url, dt in dated_links[:5]:
        print(dt.strftime("%d/%m/%Y"), "->", url)

    return dated_links[0][0]

# -----------------------------
# Download PDF
# -----------------------------
def download_file(url: str):
    # Create folder if it doesn't exist
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    filename = url.split("/")[-1]
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return

    print(f"Downloading {filename} ...")
    response = requests.get(url)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"Downloaded: {filepath}")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    latest_pdf = get_latest_pdf()
    print("Latest PDF URL:", latest_pdf)
    download_file(latest_pdf)