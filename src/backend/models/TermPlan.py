from typing import (
    ClassVar,
)

import attrs

import backend.models._base_model as bm
import backend.models.term_plan_detail


@attrs.define(kw_only=True)
class TermPlan(bm._Owned_model):

    db_table_name: ClassVar[str] = "TermPlan"
    id_column_name: ClassVar[str] = "TermPlanId"
    owner_col_id_name: ClassVar[str] = "AppliesToTerm"
    TermPlanName: str

    def __str__(self) -> str:
        return self.TermPlanName

    def entries_in_plan(self):
        yield from backend.models.term_plan_detail.TermPlanDetail.from_db(self)
