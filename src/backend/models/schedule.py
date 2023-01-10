import enum
from typing import (
    ClassVar,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.teacher
import backend.models.subject
import backend.models.class_model
import backend.models.class_room
import backend.models.institution
import backend.models.Term
import frontend.api_utils


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
    LessonId: Optional[int] = bm.ID_FIELD

    @property
    def id(self) -> Optional[int]:
        return self.LessonId

    InstitutionId: backend.models.institution.Institution = bm.main_fk_field
    WeekDay: WeekDay
    LessonStartingHour: str
    LessonEndingHour: str
    TeacherId: backend.models.teacher.Teacher
    SubjectId: backend.models.subject.Subject
    ClassId: backend.models.class_model.Class
    ClassRoomId: backend.models.class_room.ClassRoom
    InTerm: backend.models.Term.Term

    @classmethod
    def entries_in_class_room(cls, class_room, term):
        for record in frontend.api_utils.get_data(
            end_point_name="get_class_room_lessons",
            params={"class_room_id": class_room.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)

    @classmethod
    def entries_for_teacher(cls, teacher, term):
        for record in frontend.api_utils.get_data(
            end_point_name="get_teacher_lessons",
            params={"teacher_id": teacher.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)

    @classmethod
    def entries_for_class(cls, class_model, term):
        for record in frontend.api_utils.get_data(
            end_point_name="get_class_lessons",
            params={"class_id": class_model.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)

    def cols_for_insert(self) -> dict:
        res =  super().cols_for_insert()
        res["WeekDay"] = res["WeekDay"].value
        res["TeacherId"] = res["TeacherId"].id
        res["SubjectId"] = res["SubjectId"].id
        res["ClassId"] = res["ClassId"].id
        res["ClassRoomId"] = res["ClassRoomId"].id
        res["InTerm"] = res["InTerm"].id
        return res
