from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject
import backend.models.teacher
import backend.models._converters as convs_registry


@convs_registry.create_unstructuring_converters
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

    def __str__(self) -> str:
        return str(self.SubjectId)
