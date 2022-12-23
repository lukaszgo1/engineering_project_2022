import datetime
import itertools
import operator
from typing import (
    ClassVar,
    Iterator,
    Literal,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.break_model
import backend.models.class_model
import backend.models.subject
import backend.models.Term


@attrs.define(kw_only=True)
class Institution(bm._BaseModel):

    db_table_name: ClassVar[str] = "Institutions"
    id_column_name: ClassVar[str] = "InstitutionId"
    InstitutionName: str
    StartingHour: str
    EndingHour: str
    HasBreaks: Literal[0, 1]
    NormalBreakLength: Optional[int] = None
    NormalLessonLength: Optional[int] = None

    def subjects_taught_in_inst(self) -> Iterator[backend.models.subject.Subject]:
        yield from backend.models.subject.Subject.from_db(self)

    def terms_in_inst(self) -> Iterator[backend.models.Term.Term]:
        yield from backend.models.Term.Term.from_db(self)

    def term_plans_in_inst(self):
        yield from itertools.chain(*[t.plans_in_term() for t in self.terms_in_inst()])

    def classes_in_inst(self):
        yield from backend.models.class_model.Class.from_db(self)

    def lessons(self):
        if self.NormalBreakLength is None or self.NormalLessonLength is None:
            raise RuntimeError
        default_date = "2000-01-02 "
        normal_break = self.NormalBreakLength
        lesson_len = self.NormalLessonLength
        existing_breaks = list(
            backend.models.break_model.Break.from_db(self)
        )
        existing_breaks.sort(key=operator.attrgetter("BreakStartingHour"))
        break_starts = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakStartingHour}"
            ) for b in existing_breaks
        ]
        break_ends = [
            datetime.datetime.fromisoformat(
                f"{default_date}{b.BreakEndingHour}"
            ) for b in existing_breaks
        ]
        starting_hour = self.StartingHour
        ending_hour = self.EndingHour
        start_obj = datetime.datetime.fromisoformat(
            f"{default_date}{starting_hour}"
        )
        end_obj = datetime.datetime.fromisoformat(
            f"{default_date}{ending_hour}"
        )
        normal_break_td = datetime.timedelta(minutes=normal_break)
        lesson_td = datetime.timedelta(minutes=lesson_len)
        res = []
        lesson_start = start_obj 
        while lesson_start < end_obj:
            res.append(lesson_start)
            lesson_start = lesson_start + lesson_td
            possible_break_start = lesson_start
            if possible_break_start in break_starts:
                curr_break_index = break_starts.index(possible_break_start)
                long_break_duration = break_ends[curr_break_index] - break_starts[curr_break_index]
                lesson_start = lesson_start + long_break_duration
            else:
                lesson_start = lesson_start + normal_break_td
            if lesson_start >= end_obj:
                break
        return res
