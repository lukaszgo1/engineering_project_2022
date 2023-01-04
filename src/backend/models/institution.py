import datetime
import email.utils
import itertools
import operator
from typing import (
    ClassVar,
    Iterator,
    Literal,
    Optional,
)

import attrs
import requests

import backend.models._base_model as bm
import backend.models.break_model
import backend.models.class_model
import backend.models.subject
import backend.models.Term


@attrs.define(kw_only=True)
class Institution(bm._BaseModel):

    get_endpoint: ClassVar[str] = "/get_institutions"
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
