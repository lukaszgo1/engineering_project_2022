import datetime
from typing import (
    ClassVar,
    Iterator,
)

import attrs

import backend.models._base_model as bm
import backend.models.TermPlan


@attrs.define(kw_only=True)
class Term(bm._Owned_model):

    db_table_name: ClassVar[str] = "Terms"
    id_column_name: ClassVar[str] = "TermId"
    owner_col_id_name: ClassVar[str] = "TermInInst"
    StartDate: datetime.date
    EndDate: datetime.date
    TermName: str

    def plans_in_term(self) -> Iterator[backend.models.TermPlan.TermPlan]:
        yield from backend.models.TermPlan.TermPlan.from_db(self)
