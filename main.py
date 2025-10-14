from typing import Union
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import List
from models import *
import re
from functools import lru_cache

ORAR_TABLE_URL = "https://www.cs.ubbcluj.ro/files/orar/2025-1/tabelar/"

#caching the html content of the pages
@lru_cache(maxsize=300)
def get_html_content(url:str)-> str:
    '''
    get the html contents from the page located at url
    '''
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

def construct_timetable_link(href):
    '''
    constructs the link for the timetable page of a given specialisation
    based on the html file href. example input:M1.html for first year math majors
    '''
    return ORAR_TABLE_URL + href

def get_timetable_pages():
    '''
    get the a list of every available (major, year and timetable_page) that currently exists
    example of element in the output list: math,year1,link_to_math_year1_timetables_page
    '''
    soup = get_html_content(url)
    timetable_pages= []

    for row in soup.select("tr"):

        major_td = row.find("td")
        #if we are currently on the header row of the table there will be no td cells(just th)
        if not major_td:
            continue 

        #get major header
        major = major_td.get_text(strip=True)

        for link_tag in row.select("a"):
            #get existing year and timetables pages for that major and year
            href = link_tag.get("href")
            year = link_tag.get_text(strip=True)
            link=construct_timetable_link(href)

            t = TimetableLink(
                major=major,
                year=year,
                groups=get_groups_of(link),
                link=link
            )

            timetable_pages.append(t)

    return timetable_pages

def get_groups_of(link):
    '''
    get groups of a specific major and year based on the reference link
    '''
    soup=get_html_content(link)
    grupe = [h.get_text(strip=True) for h in soup.select("h1") if "Grupa" in h.get_text(strip=True)]
    return grupe

def get_group_schedule_of(link,group):
    '''
    webscrapes the table that contains the group weekly schedule
    '''
    soup=get_html_content(link)
    h1 = soup.find("h1", string=lambda t: t and re.search(group, t, re.I))
    classes=[]
    table = None
    if h1:
        for el in h1.find_all_next(["table", "h1"]):
            if el.name == "table":
                table = el
                break
            if el.name == "h1":
                break  # hit next section
    for row in table.select("tr"):
        cells = row.select("td")

        if not cells:#skipping the heading row, jumping straight to data
            continue

        ziua=cells[0].get_text(strip=True)
        orele=cells[1].get_text(strip=True)
        frecventa=cells[2].get_text(strip=True)
        sala=cells[3].get_text(strip=True)
        formatia=cells[4].get_text(strip=True)
        tipul=cells[5].get_text(strip=True)
        disciplina=cells[6].get_text(strip=True)
        cadrul_didactic=cells[7].get_text(strip=True)

        c = ClassSchedule(
            ziua=ziua,
            orele=orele,
            frecventa=frecventa,     
            sala=sala, #webscarpe these fields as well
            formatia=formatia,    
            tipul=tipul,
            disciplina=disciplina,
            cadrul_didactic=cadrul_didactic,
        )
        classes.append(c)
    
    g=GroupSchedule(
        group_name=group,
        classes=classes
    )

    return g


app = FastAPI()
url = ORAR_TABLE_URL 

@app.get("/")
def get_timetable(): #seeing all specialisations and groups
    timetables= get_timetable_pages()
    return timetables

@app.get("/schedules") #seeing all schedules for all groups
def get_timetable():
    timetables= get_timetable_pages()
    group_schdeules=[]
    for t in timetables:
        for g in t.groups:
            group_schdeules.append(get_group_schedule_of(t.link,g))
    return group_schdeules