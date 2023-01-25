from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import models._base_model as bm
import models.subject
import models.TermPlan
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class TermPlanDetail(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_termPlanDetails"
    add_endpoint: ClassVar[str] = "/add_termPlanDetail"
    delete_endpoint: ClassVar[str] = "/delete_termPlanDetail"
    edit_endpoint: ClassVar[str] = "/edit_termPlanDetail"
    db_table_name: ClassVar[str] = "TermPlanDetails"
    TermPlanDetailId: Optional[int] = bm.ID_FIELD
    TermPlanId: models.TermPlan.TermPlan = bm.main_fk_field
    LessonsAmount: int
    LessonsWeekly: int
    MinBlockSize: int
    MaxBlockSize: int
    PreferredDistanceInDays: Optional[int] = None
    PreferredDistanceInWeeks: Optional[int] = None
    SubjectId: models.subject.Subject

    @property
    def id(self) -> Optional[int]:
        return self.TermPlanDetailId
