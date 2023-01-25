"""Named differently than the class
to avoid conflicts with the `class` keyword.
"""
from typing import (
    ClassVar,
    Optional,
    TYPE_CHECKING,
)

import attrs

import models._base_model as bm
if TYPE_CHECKING:
    import models.class_to_term_plan
import models.institution
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Class(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_class"
    get_classesToTermPlan_endpoint: ClassVar[str] = "/get_classesToTermPlan"
    get_single_end_point: ClassVar[str] = "get_single_class"
    add_endpoint: ClassVar[str] = "/add_class"
    delete_endpoint: ClassVar[str] = "/delete_class"
    edit_endpoint: ClassVar[str] = "/edit_class"
    db_table_name: ClassVar[str] = "Classes"
    ClassId: Optional[int] = bm.ID_FIELD

    @property
    def id(self) -> Optional[int]:
        return self.ClassId

    ClassInInstitution: models.institution.Institution = bm.main_fk_field
    ClassIdentifier: str

    @property
    def assigned_term_plan(self) -> "Optional[models.class_to_term_plan.ClassToTermPlan]":
        import models.class_to_term_plan
        try:
            return models.class_to_term_plan.ClassToTermPlan.from_end_point_by_id(self.id)
        except bm.NonExistingEntityRequested:
            return None

    def __str__(self) -> str:
        return self.ClassIdentifier

    @classmethod
    def from_classesToTermPlan_endpoint(cls, owner):
        for record in cls.data_from_end_point(
            end_point_name=cls.get_classesToTermPlan_endpoint,
            end_point_id=str(owner.id)
        ):
            yield cls.from_json_info(record)


convs_registry.from_json_conv.register_structure_hook(
    cl=Class,
    func=lambda class_id, typ: Class.from_end_point_by_id(class_id)
)
