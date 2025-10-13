from typing import Union
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import List

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

def construct_link(href):
    return "https://www.cs.ubbcluj.ro/files/orar/2025-1/tabelar/" +href

def get_list_of_timetables():
    soup = get_soup(url)
    timetables = []

    for row in soup.select("tr"):
        major_td = row.find("td")
        if not major_td:
            continue 
        major = major_td.get_text(strip=True)
        for link_tag in row.select("a"):
            href = link_tag.get("href")
            year = link_tag.get_text(strip=True)
            link=construct_link(href)
            timetables.append({"major":major,"year": year, "reference": href, "link":link})
    return timetables

def get_classes(soup):
    grupe = [h.get_text(strip=True) for h in soup.select("h1") if "Grupa" in h.get_text(strip=True)]
    timetables=[]
    index=0
    return grupe
    '''
    for row in soup.select("tr"):
        print(index)
        grupa_curenta=grupe[index]
        index+=1
        cells = row.select("td")
        if not cells:
            continue
        ziua=cells[0].get_text(strip=True)
        orele=cells[1].get_text(strip=True)
        formatia=cells[2].get_text(strip=True)
        tipul=cells[3].get_text(strip=True)
        timetables[grupa_curenta].append(ziua,orele,formatia,tipul)
    return timetables
    '''


app = FastAPI()
url = "https://www.cs.ubbcluj.ro/files/orar/2025-1/tabelar/index.html"

@app.get("/")
def get_timetable():
    timetables= get_list_of_timetables()
    classes=[]
    for t in timetables:
        t["groups"]=get_classes(get_soup(t["link"]))
    return timetables