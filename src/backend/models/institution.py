from typing import (
    ClassVar,
    Literal,
    Optional,
)

import attrs

import backend.models._base_model as bm


@attrs.define(kw_only=True)
class Institution(bm._BaseModel):

    db_table_name: ClassVar[str] = "Institutions"
    id_column_name: ClassVar[str] = "InstitutionId"
    InstitutionName: str
    StartingHour: str
    EndingHour: str
    HasBreaks: Literal[0, 1]
    NormalBreakLength: Optional[int] = None
    NormalLessonLength: Optional[int] = None
