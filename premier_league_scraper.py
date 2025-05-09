"""
Premier League 2024-25 Data Web Scraper

This script scrapes the final league table and squad goalkeeping stats from FBref,
cleans the data, and uploads it to a Google Sheet using the GSpread API.

Dependencies:
- pandas
- requests
- beautifulsoup4
- gspread
- gspread_dataframe
- oauth2client

Kept getting a 403 error with this script
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import logging

# ----------------------------- Logging Setup -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ----------------------------- Constants -----------------------------
BASE_URL = "https://fbref.com/en/comps/9/Premier-League-Stats"
TABLE_IDS = {
    "Final Table": "results2024-202591_overall",
    "Goalkeeping": "stats_squads_keeper_for"
}
SPREADSHEET_NAME = "Premier League 2024-25 Data"

# ----------------------------- Functions -----------------------------

def fetch_html(url):
    """
    Fetches the HTML content of the given URL and returns a BeautifulSoup object.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        raise

def extract_table(soup, table_id):
    """
    Extracts an HTML table by ID and converts it to a pandas DataFrame.
    """
    table = soup.find("table", {"id": table_id})
    if not table:
        logging.error(f"Table with ID '{table_id}' not found.")
        return None
    return pd.read_html(StringIO(str(table)))[0]


def clean_dataframe(df):
    """
    Cleans common formatting issues in the DataFrame.
    """
    if df is None:
        return None
    df = df.dropna(axis=0, how='all')  # Remove empty rows
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)
    df.columns = df.columns.str.strip()
    return df


def upload_to_gsheet(df, worksheet_name):
    """
    Uploads the given DataFrame to the specified worksheet in a Google Sheet.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)

        sheet = client.open(SPREADSHEET_NAME)

        try:
            worksheet = sheet.worksheet(worksheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

        set_with_dataframe(worksheet, df)
        logging.info(f"Successfully uploaded data to worksheet: {worksheet_name}")

    except Exception as e:
        logging.error(f"Failed to upload data to Google Sheets: {e}")
        raise


# ----------------------------- Main Execution -----------------------------

def main():
    logging.info("Premier League Scraper Started")

    soup = fetch_html(BASE_URL)

    for sheet_name, table_id in TABLE_IDS.items():
        logging.info(f"Processing: {sheet_name}")
        df = extract_table(soup, table_id)
        df_cleaned = clean_dataframe(df)

        if df_cleaned is not None:
            upload_to_gsheet(df_cleaned, sheet_name)
        else:
            logging.warning(f"Skipped uploading {sheet_name} due to missing data.")

    logging.info("Scraper Finished Successfully")


if __name__ == "__main__":
    main()
