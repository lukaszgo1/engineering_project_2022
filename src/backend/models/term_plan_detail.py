from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject
import backend.models.TermPlan
import backend.models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class TermPlanDetail(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_termPlanDetails"
    db_table_name: ClassVar[str] = "TermPlanDetails"
    TermPlanDetailId: Optional[int] = bm.ID_FIELD
    TermPlanId: backend.models.TermPlan.TermPlan = bm.main_fk_field
    LessonsAmount: int
    LessonsWeekly: int
    MinBlockSize: int
    MaxBlockSize: int
    PreferredDistanceInDays: Optional[int] = None
    PreferredDistanceInWeeks: Optional[int] = None
    SubjectId: backend.models.subject.Subject

    @property
    def id(self) -> Optional[int]:
        return self.TermPlanDetailId
