"""Named differently than the class
to avoid conflicts with the `break` keyword.
"""

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
class Break(bm._Owned_model):

    @property
    def id(self) -> Optional[int]:
        return self.BreakId

    get_endpoint: ClassVar[str] = "/get_breaks"
    add_endpoint: ClassVar[str] = "/add_break"
    delete_endpoint: ClassVar[str] = "/delete_break"
    db_table_name: ClassVar[str] = "breaks"
    BreakId: Optional[int] = bm.ID_FIELD
    InstitutionId: models.institution.Institution = bm.main_fk_field
    BreakStartingHour: str
    BreakEndingHour: str
