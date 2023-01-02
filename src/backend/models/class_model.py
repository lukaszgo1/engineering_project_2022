"""Named differently than the class
to avoid conflicts with the `class` keyword.
"""
import requests
from typing import (
    ClassVar,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.class_to_term_plan


@attrs.define(kw_only=True)
class Class(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_class"
    get_classesToTermPlan_endpoint: ClassVar[str] = "/get_classesToTermPlan"
    db_table_name: ClassVar[str] = "Classes"
    id_column_name: ClassVar[str] = "ClassId"
    owner_col_id_name: ClassVar[str] = "ClassInInstitution"
    ClassIdentifier: str


    @property
    def assigned_term_plan(self) -> Optional[backend.models.class_to_term_plan.ClassToTermPlan]:
        try:
            return list(backend.models.class_to_term_plan.ClassToTermPlan.from_db(self))[0]
        except IndexError:
            return None

    def __str__(self) -> str:
        return self.ClassIdentifier

    @classmethod
    def from_classesToTermPlan_endpoint(cls, owner):
        query = requests.get('http://127.0.0.1:5000' + cls.get_classesToTermPlan_endpoint + '/' + str(owner.id))
        records_in_db = query.json()['item']
        for record in records_in_db:
            kwargs_with_vals = cls.initializer_params(record)
            kwargs_with_vals["owner"] = owner.owner  # Classes belong to the inst, not to the term
            yield cls(**kwargs_with_vals)
