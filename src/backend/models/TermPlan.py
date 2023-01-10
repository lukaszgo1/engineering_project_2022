from typing import (
    ClassVar,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.Term
import backend.models._converters as convs_registry


@attrs.define(kw_only=True)
class TermPlan(bm._Owned_model):

    @property
    def id(self):
        return self.TermPlanId

    get_endpoint: ClassVar[str] = "/get_termPlans"
    get_single_end_point: ClassVar[str] = "get_term_plan"
    db_table_name: ClassVar[str] = "TermPlan"
    TermPlanId: Optional[int] = bm.ID_FIELD
    AppliesToTerm: backend.models.Term.Term = bm.main_fk_field
    TermPlanName: str

    def __str__(self) -> str:
        return self.TermPlanName


convs_registry.from_json_conv.register_structure_hook(
    cl=TermPlan,
    func=lambda tp_id, type: TermPlan.from_end_point_by_id(tp_id)
)
