from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Subject(bm._Owned_model):

    db_table_name: ClassVar[str] = "Subjects"
    id_column_name: ClassVar[str] = "SubjectId"
    owner_col_id_name: ClassVar[str] = "TaughtIn"
    SubjectName: str
