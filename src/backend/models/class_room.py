from typing import (
    ClassVar,
    Dict,
    Optional,
    Union,
)

import attrs
import requests

import backend.models._base_model as bm
import backend.models.subject


class NoMainCourse:

    id = None

    def __str__(self) -> str:
        return "brak"


@attrs.define(kw_only=True)
class ClassRoom(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_classRooms"
    db_table_name: ClassVar[str] = "ClassRooms"
    id_column_name: ClassVar[str] = "ClassRoomId"
    owner_col_id_name: ClassVar[str] = "IsIn"
    ClassRoomIdentifier: str
    MainSubjectId: Optional[int] = attrs.field(
        default=None,
        metadata={bm.USER_PRESENTABLE_FIELD_NAME: False}
    )
    PrimaryCourse: Optional[
        Union[backend.models.subject.Subject, NoMainCourse]
            ] = None

    def __attrs_post_init__(self):
        if self.MainSubjectId is not None:
            if self.PrimaryCourse is None:
                for subj in backend.models.subject.Subject.from_db(self.owner):
                    if subj.id == self.MainSubjectId:
                        self.PrimaryCourse = subj
                        break
                else:
                    raise RuntimeError("Failed to find the subject in db")
        else:
            self.PrimaryCourse = NoMainCourse()

    def cols_for_insert(self) -> Dict:
        res = super().cols_for_insert()
        res["PrimaryCourse"] = res["PrimaryCourse"].id
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
        res["MainSubjectId"] = res["PrimaryCourse"]
        del res["PrimaryCourse"]
        return res

    def __str__(self) -> str:
        return self.ClassRoomIdentifier

    @classmethod
    def from_class_room_for_subj_end_point(cls, subj_model):
        # All class rooms are placed
        # in the same institution as the subject
        class_room_owner = subj_model.owner
        query = requests.get(
            f"http://127.0.0.1:5000/get_ClassRoomsForSubject/{str(subj_model.id)}"
        )
        records_in_db = query.json()['item']
        for record in records_in_db:
            kwargs_with_vals = cls.initializer_params(record)
            kwargs_with_vals["owner"] = class_room_owner
            yield cls(**kwargs_with_vals)
