import pandas as pd
import logging
from bs4 import BeautifulSoup
from urllib.request import urlopen
from io import StringIO

# Using this script to test the Web Scraper 

# Web Scraping 
url = "https://fbref.com/en/comps/9/Premier-League-Stats"

try:
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "lxml")
    league_table = soup.find("table", {"id": "results2024-202591_overall"})

    if league_table is None:
        raise ValueError("League table not found in the HTML.")

    df = pd.read_html(StringIO(str(league_table)))[0]
except Exception as e:
    logging.error(f"Failed to scrape or parse league table: {e}")
    raise Exception("Scraping failed. Check if the table ID or URL has changed.")

# Find all tables and print their IDs
tables = soup.find_all("table")
for table in tables:
    print(table.get("id"))
