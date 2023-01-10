from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject
import backend.models.teacher


@attrs.define(kw_only=True)
class TeacherToSubject(bm._Owned_model):

    db_table_name: ClassVar[str] = "TeachersToSubjects"
    get_endpoint: ClassVar[str] = "get_teachersToSubjects"
    TeacherToSubjectId: Optional[int] = bm.ID_FIELD
    TeacherId: backend.models.teacher.Teacher = bm.main_fk_field
    SubjectId: backend.models.subject.Subject

    @property
    def id(self) -> Optional[int]:
        return self.TeacherToSubjectId

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

    def __str__(self) -> str:
        return str(self.SubjectId)
