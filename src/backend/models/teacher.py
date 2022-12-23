from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Teacher(bm._Owned_model):

    db_table_name: ClassVar[str] = "Teachers"
    id_column_name: ClassVar[str] = "TeacherId"
    owner_col_id_name: ClassVar[str] = "EmployedIn"
    FirstName: str
    LastName: str
    IsAvailable: bool

    def __str__(self) -> str:
        return f"{self.FirstName} {self.LastName}"
