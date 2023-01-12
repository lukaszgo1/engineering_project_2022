from typing import (
    ClassVar,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models._converters as convs_registry
import backend.models.institution


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Subject(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_subjects"
    get_subjectsForClass_endpoint: ClassVar[str] = "/get_subjectsForClass"
    get_single_end_point: ClassVar[str] = "get_subject"
    db_table_name: ClassVar[str] = "Subjects"
    SubjectId: Optional[int] = bm.ID_FIELD
    TaughtIn: backend.models.institution.Institution = bm.main_fk_field
    SubjectName: str

    @property
    def id(self) -> Optional[int]:
        return self.SubjectId

    def __str__(self) -> str:
        return self.SubjectName

    @classmethod
    def from_subjects_for_class_endpoint(cls, class_model):
        for record in cls.data_from_end_point(
            end_point_name=cls.get_subjectsForClass_endpoint,
            end_point_id=str(class_model.id)
        ):
            yield cls.from_json_info(record)

    @classmethod
    def get_not_assigned_to_teacher(cls, teacher_model):
        for record in cls.data_from_end_point(
            end_point_name="get_Teachers_not_assigned_to",
            end_point_id=str(teacher_model.id)
        ):
            yield cls.from_json_info(record)


convs_registry.from_json_conv.register_structure_hook(
    cl=Subject,
    func=lambda subj_id, type: Subject.from_end_point_by_id(subj_id)
)
