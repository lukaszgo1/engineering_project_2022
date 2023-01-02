from typing import (
    ClassVar,
)
import requests
import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Subject(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_subjects"
    get_subjectsForClass_endpoint: ClassVar[str] = "/get_subjectsForClass"
    db_table_name: ClassVar[str] = "Subjects"
    id_column_name: ClassVar[str] = "SubjectId"
    owner_col_id_name: ClassVar[str] = "TaughtIn"
    SubjectName: str

    def __str__(self) -> str:
        return self.SubjectName

    @classmethod
    def from_subjects_for_class_endpoint(cls, class_model):
        # All subjects belong to the same institution as the class
        subj_owner = class_model.owner
        query = requests.get(
            f"http://127.0.0.1:5000{cls.get_subjectsForClass_endpoint}/{str(class_model.id)}"
        )
        records_in_db = query.json()['item']
        for record in records_in_db:
            kwargs_with_vals = cls.initializer_params(record)
            kwargs_with_vals["owner"] = subj_owner
            yield cls(**kwargs_with_vals)
