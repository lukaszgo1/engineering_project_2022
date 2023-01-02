from typing import (
    ClassVar,
)

import attrs
import requests

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Teacher(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_teachers"
    db_table_name: ClassVar[str] = "Teachers"
    id_column_name: ClassVar[str] = "TeacherId"
    owner_col_id_name: ClassVar[str] = "EmployedIn"
    FirstName: str
    LastName: str
    IsAvailable: bool

    def __str__(self) -> str:
        return f"{self.FirstName} {self.LastName}"

    @classmethod
    def from_teachers_for_subjs_end_point(cls, subj_model):
        # All teachers are employed
        # in the same institution as the subject
        teacher_owner = subj_model.owner
        query = requests.get(
            f"http://127.0.0.1:5000/get_TeachersForSubject/{str(subj_model.id)}"
        )
        records_in_db = query.json()['item']
        for record in records_in_db:
            kwargs_with_vals = cls.initializer_params(record)
            kwargs_with_vals["owner"] = teacher_owner
            yield cls(**kwargs_with_vals)
