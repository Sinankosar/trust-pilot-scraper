import requests
from bs4 import BeautifulSoup
import time
import random
import mysql.connector

conn = mysql.connector.connect(
    user="root",
    host="localhost",
    password="mysql123",
    database="restaurants"
)
cursor = conn.cursor()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

url = "https://www.trustpilot.com/categories/restaurants_bars"
BASE_URL = "https://www.trustpilot.com"


def get_datas(url):
    print("Scraping:", url)
    time.sleep(2)
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        print("Status:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    products = soup.find_all(
        "div",
        class_="CDS_Card_card__485220 styles_card__WMwue"
    )

    for product in products:
        try:
            name = (
                product
                .find("a")
                .find("div")
                .find_all("div")[1]
                .find_all("p")[1]
                .text
            )

            link = (
                product
                .find("a")
                .find("div")
                .find_all("div")[1]
                .find_all("p")[2]
                .text
            )

            stars = (
                product
                .find("a")
                .find("div")
                .find_all("div")[1]
                .find_all("div")[-1]
                .find("p")
                .find_all("span")[1]
                .text
            )

            views = (
                product
                .find("a")
                .find("div")
                .find_all("div")[1]
                .find_all("div")[-1]
                .find("p")
                .find_all("span")[3]
                .text
            )

            address = (
                product
                .find("a")
                .find("div")
                .find_all("div")[-1]
                .text
            )

            sql = """
                INSERT INTO restaurant_table
                (name, stars, views, url, address)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, stars, views, link, address))
            conn.commit()

            print("Added:", name)

        except Exception as e:
            print("Error:", e)
            continue

    next_page = soup.find(
        "div",
        class_="styles_paginationWrapper__uPv3Y categorylayout_pagination__lHYaN"
    )

    if next_page:
        nav = next_page.find("nav")
        if nav:
            links = nav.find_all("a")
            if links:
                last_link = links[-1]
                if last_link.text.strip() == "Next page" and last_link.get("href"):
                    return BASE_URL + last_link["href"]

    return None


while url:
    time.sleep(random.uniform(1, 3))
    url = get_datas(url)

print("Complated")
