from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject


@attrs.define(kw_only=True)
class TermPlanDetail(bm._Owned_model):

    db_table_name: ClassVar[str] = "TermPlanDetails"
    id_column_name: ClassVar[str] = "TermPlanDetailId"
    owner_col_id_name: ClassVar[str] = "TermPlanId"
    LessonsAmount: int
    MinBlockSize: int
    MaxBlockSize: int
    PreferredDistanceInDays: Optional[int] = None
    PreferredDistanceInWeeks: Optional[int] = None
    EntryDescribingSubjectId: int = attrs.field(
        metadata={bm.USER_PRESENTABLE_FIELD_NAME: False}
    )
    SubjectId: Optional[
        backend.models.subject.Subject
    ] = None

    def __attrs_post_init__(self):
        if self.SubjectId is None:
            for subj in self.owner.owner.owner.subjects_taught_in_inst():
                if subj.id == self.EntryDescribingSubjectId:
                    self.SubjectId = subj
                    break
            else:
                raise RuntimeError("Failed to find the subject in db")

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

    @classmethod
    def initializer_params(cls, db_record: Dict) -> Dict:
        res = super().initializer_params(db_record)
        res["EntryDescribingSubjectId"] = res["SubjectId"]
        del res["SubjectId"]
        return res
