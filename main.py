from typing import Union
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import List

def scrape_table_of_timetables():
    url = "https://www.cs.ubbcluj.ro/files/orar/2025-1/tabelar/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    timetables = []
    majors = []

    for row in soup.select("tr"):
        major_td = row.find("td")
        if not major_td:
            continue 
        major = major_td.get_text(strip=True)
        for link_tag in row.select("a"):
            href = link_tag.get("href")
            year = link_tag.get_text(strip=True)
            timetables.append({"major":major,"year": year, "reference": href})
    return timetables


app = FastAPI()

@app.get("/timetable")
def get_timetable():
    return scrape_table_of_timetables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}