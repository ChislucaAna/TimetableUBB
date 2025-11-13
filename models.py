from pydantic import BaseModel, Field
from typing import List

class TimetableLink(BaseModel):
    """Model representing a timetable link for a major and year"""
    major: str = Field(..., description="The major/specialization name")
    year: str = Field(..., description="The academic year (e.g., 'Year 1', 'Year 2')")
    groups: List[str] = Field(..., description="List of available groups for this major and year")
    link: str = Field(..., description="URL to the timetable page")

class ClassSchedule(BaseModel):
    """Model representing a single class in the schedule"""
    ziua: str = Field(..., description="Day of the week (e.g., 'Luni', 'Marti')")
    orele: str = Field(..., description="Time slot (e.g., '08:00-10:00')")
    frecventa: str = Field(..., description="Frequency (e.g., 'Saptamanal', 'Saptamana 1,3')")
    sala: str = Field(..., description="Room/classroom number")
    formatia: str = Field(..., description="Formation type (e.g., 'Curs', 'Seminar', 'Laborator')")
    tipul: str = Field(..., description="Type of class (e.g., 'Obligatoriu', 'Optional')")
    disciplina: str = Field(..., description="Subject/course name")
    cadrul_didactic: str = Field(..., description="Teaching staff name")

class GroupSchedule(BaseModel):
    """Model representing the complete schedule for a group"""
    group_name: str = Field(..., description="Name of the group (e.g., 'Grupa 1', 'Grupa 2')")
    classes: List[ClassSchedule] = Field(..., description="List of all classes for this group")
    
