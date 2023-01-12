from typing import (
    ClassVar,
    Dict,
    Optional,
    Union,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject
import backend.models.institution
import backend.models._converters as convs_registry


class NoMainCourse:

    id = None

    def __str__(self) -> str:
        return "brak"


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class ClassRoom(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_classRooms"
    get_single_end_point: ClassVar[str] = "get_single_class_room"
    db_table_name: ClassVar[str] = "ClassRooms"
    ClassRoomId: Optional[int] = bm.ID_FIELD
    IsIn: backend.models.institution.Institution = bm.main_fk_field
    ClassRoomIdentifier: str
    PrimaryCourse: Union[backend.models.subject.Subject, NoMainCourse]

    @property
    def id(self) -> Optional[int]:
        return self.ClassRoomId

    def __str__(self) -> str:
        return self.ClassRoomIdentifier

    @classmethod
    def from_class_room_for_subj_end_point(cls, subj_model):
        for record in cls.data_from_end_point(
            end_point_name="get_ClassRoomsForSubject",
            end_point_id=str(subj_model.id)
        ):
            yield cls.from_json_info(record)

def _get_main_subj_from_id(subj_id: Optional[int], typ):
    if subj_id is None:
        return NoMainCourse()
    return backend.models.subject.Subject.from_end_point_by_id(subj_id)


convs_registry.from_json_conv.register_structure_hook(
    cl=Union[backend.models.subject.Subject, NoMainCourse],
    func=_get_main_subj_from_id
)

convs_registry.from_json_conv.register_structure_hook(
    cl=ClassRoom,
    func=lambda cr_id, typ: ClassRoom.from_end_point_by_id(cr_id)
)
