import dataclasses
from typing import (
    ClassVar,
    Literal,
    Optional,
    Union,
)

import backend.models._base_model as bm


@dataclasses.dataclass
class Institution(bm._BaseModel):

    db_table_name: ClassVar[str] = "Institutions"
    id_column_name: ClassVar[str] = "InstitutionId"
    InstitutionName: str
    StartingHour: str
    EndingHour: str
    HasBreaks: Literal[0, 1]
    NormalBreakLength: Optional[int] = None
    NormalLessonLength: Optional[int] = None
    id: Union[int, Literal[bm.NOT_YET_INSERTED]] = bm.NOT_YET_INSERTED
