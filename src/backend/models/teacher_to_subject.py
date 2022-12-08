from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject


@attrs.define(kw_only=True)
class TeacherToSubject(bm._Owned_model):

    db_table_name: ClassVar[str] = "TeachersToSubjects"
    id_column_name: ClassVar[str] = "TeacherToSubjectId"
    owner_col_id_name: ClassVar[str] = "TeacherId"
    AssignedSubjectId: Optional[int] = attrs.field(
        default=None,
        metadata={bm.USER_PRESENTABLE_FIELD_NAME: False}
    )
    SubjectId: Optional[
        backend.models.subject.Subject
    ] = None

    def __attrs_post_init__(self):
        if self.AssignedSubjectId is not None:
            if self.SubjectId is None:
                for subj in backend.models.subject.Subject.from_db(
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
