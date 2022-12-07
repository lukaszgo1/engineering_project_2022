from typing import (
    ClassVar,
    Dict,
    Optional,
    Union,
)

import attrs

import backend.models._base_model as bm
import backend.models.subject


class NoMainCourse:

    id = None

    def __str__(self) -> str:
        return "brak"


@attrs.define(kw_only=True)
class ClassRoom(bm._Owned_model):

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

    @classmethod
    def initializer_params(cls, db_record: Dict) -> Dict:
        res = super().initializer_params(db_record)
        res["MainSubjectId"] = res["PrimaryCourse"]
        del res["PrimaryCourse"]
        print(res)
        return res
