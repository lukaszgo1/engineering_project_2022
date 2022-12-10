import datetime
from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Term(bm._Owned_model):

    db_table_name: ClassVar[str] = "Terms"
    id_column_name: ClassVar[str] = "TermId"
    owner_col_id_name: ClassVar[str] = "TermInInst"
    StartDate: datetime.date
    EndDate: datetime.date
    TermName: str
