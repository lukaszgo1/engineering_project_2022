from typing import (
    ClassVar,
    Optional,
)

import attrs

import models._base_model as bm
import models.institution
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Teacher(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_teachers"
    get_single_end_point: ClassVar[str] = "get_teacher"
    add_endpoint: ClassVar[str] = "/add_teacher"
    delete_endpoint: ClassVar[str] = "/delete_teacher"
    edit_endpoint: ClassVar[str] = "/edit_teacher"
    db_table_name: ClassVar[str] = "Teachers"
    TeacherId: Optional[int] = bm.ID_FIELD
    EmployedIn: models.institution.Institution = bm.main_fk_field
    FirstName: str
    LastName: str
    IsAvailable: bool

    @property
    def id(self) -> Optional[int]:
        return self.TeacherId

    def __str__(self) -> str:
        return f"{self.FirstName} {self.LastName}"

    @classmethod
    def from_teachers_for_subjs_end_point(cls, subj_model):
        for record in cls.data_from_end_point(
            end_point_name="get_TeachersForSubject",
            end_point_id=str(subj_model.id)
        ):
            yield cls.from_json_info(record)


convs_registry.from_json_conv.register_structure_hook(
    cl=Teacher,
    func=lambda teacher_id, type: Teacher.from_end_point_by_id(teacher_id)
)
