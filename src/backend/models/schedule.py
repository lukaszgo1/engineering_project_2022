import enum
from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm
import backend.models.teacher
import backend.models.subject
import backend.models.class_model
import backend.models.class_room
import backend.models.Term


@enum.unique
class WeekDay(enum.IntEnum):

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    def __str__(self) -> str:
        return {
            WeekDay.MONDAY: "Poniedziałek",
            WeekDay.TUESDAY: "Wtorek",
            WeekDay.WEDNESDAY: "Środa",
            WeekDay.THURSDAY: "Czwartek",
            WeekDay.FRIDAY: "Piątek",
            WeekDay.SATURDAY: "Sobota",
            WeekDay.SUNDAY: "Niedziela"
        }[self]


@attrs.define(kw_only=True)
class Schedule(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_class"
    post_endpoint: ClassVar[str] = "/add_schedule"
    db_table_name: ClassVar[str] = "Schedule"
    id_column_name: ClassVar[str] = "LessonId"
    owner_col_id_name: ClassVar[str] = "InstitutionId"
    WeekDay: WeekDay
    LessonStartingHour: str
    LessonEndingHour: str
    TeacherId: backend.models.teacher.Teacher
    SubjectId: backend.models.subject.Subject
    ClassId: backend.models.class_model.Class
    ClassRoomId: backend.models.class_room.ClassRoom
    InTerm: backend.models.Term.Term

    def cols_for_insert(self) -> dict:
        res =  super().cols_for_insert()
        res["WeekDay"] = res["WeekDay"].value
        res["TeacherId"] = res["TeacherId"].id
        res["SubjectId"] = res["SubjectId"].id
        res["ClassId"] = res["ClassId"].id
        res["ClassRoomId"] = res["ClassRoomId"].id
        res["InTerm"] = res["InTerm"].id
        return res
