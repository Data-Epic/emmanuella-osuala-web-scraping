from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup, Comment

class PremierLeagueScraper:
    def __init__(self, driver_path):
        options = Options()
        options.add_argument("--headless")
        options.set_preference("general.useragent.override", "Mozilla/5.0")

        service = Service(driver_path)
        self.driver = webdriver.Firefox(service=service, options=options)

    def scrape_overviewtable(self):
        try:
            self.driver.get("https://fbref.com/en/comps/9/Premier-League-Stats")
            time.sleep(10)  # Waiting for JS to load

            # Getting the full page HTML
            html = self.driver.page_source

            with open("page.html", "w", encoding="utf-8") as f:
                 f.write(html)

            soup = BeautifulSoup(html, "html.parser")

            # Searching within HTML comments for the hidden table
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))

            table_soup = None
            for comment in comments:
                if "results2024" in comment and "table" in comment:
                    comment_soup = BeautifulSoup(comment, "lmxl")
                    table_soup = comment_soup.find("table", {"id": "results2024-202591_overall"})
                    break

            if table_soup is None:
                print("❌ Table not found in HTML comments.")
                return

            headers = [th.text for th in table_soup.find("thead").find_all("th")]
            rows = table_soup.find("tbody").find_all("tr")

            data = []
            for i, row in enumerate(rows):
                rk = row.find("th").text
                cells = [td.text for td in row.find_all("td")]
                full_row = [rk] + cells
                if len(full_row) != len(headers):
                    continue
                data.append(full_row)

            df = pd.DataFrame(data, columns=headers)

            df.rename(columns={
                "Rk": "Rank", "Squad": "Team", "MP": "Matches Played", "W": "Wins", "D": "Draws", "L": "Losses",
                "GF": "Goals For", "GA": "Goals Against", "GD": "Goal Difference", "Pts": "Points",
                "Pts/MP": "Points/Match", "xG": "Expected Goals", "xGA": "Expected Goals Allowed",
                "xGD": "Expected Goal Difference", "xGD/90": "xGD per 90", "Last 5": "Last 5 Matches",
                "Attendance": "Attendance per Game", "Team Top Scorer": "Top Scorer",
                "Goalkeeper": "Main Goalkeeper"
            }, inplace=True)

            if "Notes" in df.columns:
                df.drop(columns="Notes", inplace=True)

            print(df)

        except Exception as e:
            print(f"❌ An error occurred during scraping: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = PremierLeagueScraper(driver_path="geckodriver.exe")
    scraper.scrape_overviewtable()
