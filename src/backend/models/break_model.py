"""Named differently than the class
to avoid conflicts with the `break keyword.
"""

from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Break(bm._Owned_model):

    db_table_name: ClassVar[str] = "breaks"
    id_column_name: ClassVar[str] = "BreakId"
    owner_col_id_name: ClassVar[str] = "InstitutionId"
    BreakStartingHour: str
    BreakEndingHour: str
