from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.TermPlan


@attrs.define(kw_only=True)
class ClassToTermPlan(bm._Owned_model):

    db_table_name: ClassVar[str] = "ClassToTermPlan"
    id_column_name: ClassVar[str] = "ClassToTermPlanId"
    owner_col_id_name: ClassVar[str] = "ClassId"
    AssociatedTermPlanId: Optional[int] = attrs.field(
        default=None,
        metadata={bm.USER_PRESENTABLE_FIELD_NAME: False}
    )
    TermPlanId: Optional[
        backend.models.TermPlan.TermPlan
    ] = None

    def __attrs_post_init__(self):
        if self.AssociatedTermPlanId is not None:
            if self.TermPlanId is None:
                owning_inst = self.owner.owner
                for tp in owning_inst.term_plans_in_inst():
                    if tp.id == self.AssociatedTermPlanId:
                        self.TermPlanId= tp
                        break
                else:
                    raise RuntimeError("Failed to find term plan in DB")

    def cols_for_insert(self) -> dict:
        res = super().cols_for_insert()
        res["TermPlanId"] = self.AssociatedTermPlanId
        return res

    @classmethod
    def initializer_params(cls, db_record: dict) -> dict:
        res = super().initializer_params(db_record)
        res["AssociatedTermPlanId"] = res.pop("TermPlanId")
        return res

    def __str__(self) -> str:
        return str(self.TermPlanId)
