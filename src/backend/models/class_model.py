"""Named differently than the class
to avoid conflicts with the `class` keyword.
"""

from typing import (
    ClassVar,
    Optional,
)

import attrs

import backend.models._base_model as bm
import backend.models.class_to_term_plan


@attrs.define(kw_only=True)
class Class(bm._Owned_model):

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
