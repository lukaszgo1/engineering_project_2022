from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject
import backend.models.TermPlan


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

    def cols_for_insert(self) -> Dict:
        res = super().cols_for_insert()
        res["SubjectId"] = self.EntryDescribingSubjectId
        return res

    def update_db_record(self, new_values: Dict) -> None:
        chosen_subject_model = new_values["SubjectId"]
        new_values["SubjectId"] = chosen_subject_model.id
        super().update_db_record(new_values)
        self.EntryDescribingSubjectId = chosen_subject_model.id
        self.SubjectId = chosen_subject_model
