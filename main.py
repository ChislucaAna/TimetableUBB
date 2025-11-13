from fastapi import FastAPI, Query, HTTPException
import requests
from bs4 import BeautifulSoup
from models import *
import re
from functools import lru_cache
from typing import List

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


app = FastAPI(
    title="UBB Timetable API",
    description="API for retrieving university timetables from UBB Cluj-Napoca Computer Science faculty",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

url = ORAR_TABLE_URL 

@app.get(
    "/",
    tags=["Timetables"],
    summary="Get all available timetables",
    description="Retrieve a list of all available majors, years, groups, and their timetable links",
    response_model=List[TimetableLink]
)
def get_timetable():
    """
    Get all available specializations and groups.
    
    Returns a list of TimetableLink objects containing:
    - major: The major/specialization name
    - year: The academic year
    - groups: List of available groups for that major/year
    - link: URL to the timetable page
    """
    timetables = get_timetable_pages()
    return timetables

@app.get(
    "/schedules",
    tags=["Schedules"],
    summary="Get all group schedules",
    description="Retrieve the complete schedule for all groups across all majors and years",
    response_model=List[GroupSchedule]
)
def get_all_schedules():
    """
    Get schedules for all groups.
    
    This endpoint fetches and returns the complete timetable schedule
    for every group in every major and year. Note: This may take a while
    to process as it scrapes data for all groups.
    
    Returns a list of GroupSchedule objects, each containing:
    - group_name: The name of the group
    - classes: List of ClassSchedule objects with class details
    """
    timetables = get_timetable_pages()
    group_schedules = []
    for t in timetables:
        for g in t.groups:
            group_schedules.append(get_group_schedule_of(t.link, g))
    return group_schedules

@app.get(
    "/schedule",
    tags=["Schedules"],
    summary="Get schedule for a specific group",
    description="Retrieve the timetable schedule for a specific group by major, year, and group name",
    response_model=GroupSchedule,
    responses={
        200: {
            "description": "Successfully retrieved group schedule",
            "content": {
                "application/json": {
                    "example": {
                        "group_name": "Grupa 1",
                        "classes": [
                            {
                                "ziua": "Luni",
                                "orele": "08:00-10:00",
                                "frecventa": "Saptamanal",
                                "sala": "A101",
                                "formatia": "Curs",
                                "tipul": "Obligatoriu",
                                "disciplina": "Programare",
                                "cadrul_didactic": "Prof. X"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "Group or timetable not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Group 'Grupa 1' not found for Math Year 1. Available groups: ['Grupa 2', 'Grupa 3']"
                    }
                }
            }
        }
    }
)
def get_group_schedule(
    group: str = Query(..., description="The group name (e.g., 'Grupa 1', 'Grupa 2')")
):
    """
    Get the timetable schedule for a specific group.
    
    **Parameters:**
    - **group**: The group name (e.g., "Grupa 1", "Grupa 2")
    
    **Returns:**
    - GroupSchedule object containing the group name and list of classes
    
    **Errors:**
    - Returns 404 error if the major/year combination is not found
    - Returns 404 error if the group doesn't exist for the specified major/year
    """
    timetables = get_timetable_pages()

    
    # Find the timetable link for the specified major and year
    for t in timetables:
        if group in t.groups:
            return get_group_schedule_of(t.link, group)
        else:
            continue


    raise HTTPException(
        status_code=404,
        detail=f"Group '{group}' not found."
    )