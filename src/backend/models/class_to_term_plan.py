from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.TermPlan
import backend.models.class_model
import backend.models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class ClassToTermPlan(bm._Owned_model):

    db_table_name: ClassVar[str] = "ClassToTermPlan"
    get_single_end_point: ClassVar[str] = "get_class_to_term_plan"
    ClassToTermPlanId: Optional[int] = bm.ID_FIELD
    ClassId: backend.models.class_model.Class = bm.main_fk_field
    TermPlanId: backend.models.TermPlan.TermPlan

    # This model is pretty specific,
    # since a single class can have only one term plan assigned,
    # which in turn means that selecting all records
    # always returns a single one.
    #  For now just omit the end point for retrieving all records.

    @property
    def id(self) -> Optional[int]:
        return self.ClassToTermPlanId

    def __str__(self) -> str:
        return str(self.TermPlanId)
