from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.TermPlan


@attrs.define(kw_only=True)
class TermPlanToClass(bm._Owned_model):

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
                for tp in backend.models.TermPlan.TermPlan.from_db(
                    self.owner.owner
                ):
                    if subj.id == self.AssignedSubjectId:
                        self.SubjectId = subj
                        break
                else:
                    raise RuntimeError("Failed to find the subject in db")

    def cols_for_insert(self) -> Dict:
        res = super().cols_for_insert()
        res["SubjectId"] = self.AssignedSubjectId
        return res

    def update_db_record(self, new_values: Dict) -> None:
        chosen_subject_model = new_values["PrimaryCourse"]
        new_values["PrimaryCourse"] = chosen_subject_model.id
        del new_values["MainSubjectId"]
        super().update_db_record(new_values)
        self.MainSubjectId = chosen_subject_model.id
        self.PrimaryCourse = chosen_subject_model

    @classmethod
    def initializer_params(cls, db_record: Dict) -> Dict:
        res = super().initializer_params(db_record)
        res["AssignedSubjectId"] = res["SubjectId"]
        del res["SubjectId"]
        return res

    def __str__(self) -> str:
        return str(self.SubjectId)
