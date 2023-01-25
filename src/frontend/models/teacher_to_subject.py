from typing import (
    ClassVar,
    Dict,
    Optional,
)

import attrs

import models._base_model as bm
import models.subject
import models.teacher
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class TeacherToSubject(bm._Owned_model):

    db_table_name: ClassVar[str] = "TeachersToSubjects"
    get_endpoint: ClassVar[str] = "get_teachersToSubjects"
    add_endpoint: ClassVar[str] = "/add_teacherToSubject"
    delete_endpoint: ClassVar[str] = "/delete_teacherToSubject"
    TeacherToSubjectId: Optional[int] = bm.ID_FIELD
    TeacherId: models.teacher.Teacher = bm.main_fk_field
    SubjectId: models.subject.Subject

    @property
    def id(self) -> Optional[int]:
        return self.TeacherToSubjectId

    def __str__(self) -> str:
        return str(self.SubjectId)
