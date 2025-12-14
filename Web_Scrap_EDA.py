import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "http://quotes.toscrape.com/"
START_PAGE = "/page/1/"


# Extraction of data from a website
def scrape_quotes():
    quotes_data = []
    next_page = START_PAGE
    visited_pages = set()

    while next_page:
        if next_page in visited_pages:
            print(f"Detected a  loop at {next_page}, exiting...")
            break
        visited_pages.add(next_page)

        url = BASE_URL + next_page
        print(f"Scraping {url}")

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request Failed:{e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")

        if not quotes:
            print(f"No quotes found on {url}, exiting...")
            break

        for quote in quotes:
            try:
                text = quote.find("span", class_="text").get_text(strip=True)
                author = quote.find("small", class_="author").get_text(strip=True)
                tags = [
                    tag.get_text(strip=True)
                    for tag in quote.find_all("a", class_="tag")
                ]
                quotes_data.append(
                    {"Quote": text, "Author": author, "Tags": ",".join(tags)}
                )
            except AttributeError as e:
                print(f"Error parsing quote block: {e}")
                continue

        next_btn = soup.find("li", class_="next")
        next_page = next_btn.find("a")["href"] if next_btn else None

        return quotes_data

    # Store data in CSV file
    def save_to_csv(data, filename="quotes.csv"):
        if not data:
            print("No data to save.")
            return

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Quote", "Author", "Tags"])
                writer.writeheader()
                writer.writerows(data)
            print(f"Saved {len(data)} quotes to {filename}")
        except Exception as e:
            print(f"Failed to save file: {e}")

    if __name__ == "__main__":
        scrap_data = scrape_quotes()
        save_to_csv(scrap_data)

        import pandas as pd

        file_path = "quotes.csv"
        data = pd.read_csv(file_path)
        data.head()

        # Word Cloud Visualization
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        all_quotes = " ".join(data["Quote"].dropna())
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
            all_quotes
        )

        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
