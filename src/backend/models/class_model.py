"""Named differently than the class
to avoid conflicts with the `class` keyword.
"""

from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Class(bm._Owned_model):

    db_table_name: ClassVar[str] = "Classes"
    id_column_name: ClassVar[str] = "ClassId"
    owner_col_id_name: ClassVar[str] = "ClassInInstitution"
    ClassIdentifier: str
