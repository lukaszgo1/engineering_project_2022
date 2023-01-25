from typing import (
    ClassVar,
    Optional,
)

import attrs

import models._base_model as bm
import models.Term
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class TermPlan(bm._Owned_model):

    @property
    def id(self):
        return self.TermPlanId

    get_endpoint: ClassVar[str] = "/get_termPlans"
    get_single_end_point: ClassVar[str] = "get_term_plan"
    add_endpoint: ClassVar[str] = "/add_termPlan"
    delete_endpoint: ClassVar[str] = "/delete_termPlan"
    edit_endpoint: ClassVar[str] = "/edit_termPlan"
    db_table_name: ClassVar[str] = "TermPlan"
    TermPlanId: Optional[int] = bm.ID_FIELD
    AppliesToTerm: models.Term.Term = bm.main_fk_field
    TermPlanName: str

    def __str__(self) -> str:
        return self.TermPlanName


convs_registry.from_json_conv.register_structure_hook(
    cl=TermPlan,
    func=lambda tp_id, type: TermPlan.from_end_point_by_id(tp_id)
)
