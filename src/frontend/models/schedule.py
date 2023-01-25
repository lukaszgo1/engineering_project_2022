import enum
from typing import (
    ClassVar,
    Optional,
)

import attrs

import models._base_model as bm
import models.teacher
import models.subject
import models.class_model
import models.class_room
import models.institution
import models.Term
import api_utils
import models._converters as convs_registry


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


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Schedule(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_class"
    add_endpoint: ClassVar[str] = "/add_schedule"
    delete_endpoint: ClassVar[str] = "/delete_schedule"
    db_table_name: ClassVar[str] = "Schedule"
    LessonId: Optional[int] = bm.ID_FIELD

    @property
    def id(self) -> Optional[int]:
        return self.LessonId

    InstitutionId: models.institution.Institution = bm.main_fk_field
    WeekDay: WeekDay
    LessonStartingHour: str
    LessonEndingHour: str
    TeacherId: models.teacher.Teacher
    SubjectId: models.subject.Subject
    ClassId: models.class_model.Class
    ClassRoomId: models.class_room.ClassRoom
    InTerm: models.Term.Term

    @classmethod
    def entries_in_class_room(cls, class_room, term):
        for record in api_utils.get_data(
            end_point_name="get_class_room_lessons",
            params={"class_room_id": class_room.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)

    @classmethod
    def entries_for_teacher(cls, teacher, term):
        for record in api_utils.get_data(
            end_point_name="get_teacher_lessons",
            params={"teacher_id": teacher.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)

    @classmethod
    def entries_for_class(cls, class_model, term):
        for record in api_utils.get_data(
            end_point_name="get_class_lessons",
            params={"class_id": class_model.id, "term_id": term.id}
        )["item"]:
            yield cls.from_json_info(record)
