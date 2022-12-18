from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class TermPlan(bm._Owned_model):

    db_table_name: ClassVar[str] = "TermPlan"
    id_column_name: ClassVar[str] = "TermPlanId"
    owner_col_id_name: ClassVar[str] = "AppliesToTerm"
    TermPlanName: str