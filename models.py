from pydantic import BaseModel
from typing import List, Dict

class TimetableLink(BaseModel): #used for main menu UI in the app-selecting ur group and stuff
    major: str
    year: str
    groups:list
    link: str

class ClassSchedule(BaseModel):
    ziua: str
    orele: str
    frecventa:str
    sala:str
    formatia: str
    tipul: str
    disciplina:str
    cadrul_didactic:str

class GroupSchedule(BaseModel): #used for the display of the timetable the user wants
    group_name: str
    classes: List[ClassSchedule]
    
