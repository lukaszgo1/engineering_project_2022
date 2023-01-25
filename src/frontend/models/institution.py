import itertools
from typing import (
    ClassVar,
    Iterator,
    Literal,
    Optional,
    TYPE_CHECKING,
)

import attrs

import models._base_model as bm
if TYPE_CHECKING:
    import models.subject
    import models.Term
import models._converters as convs_registry


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Institution(bm._BaseModel):

    get_endpoint: ClassVar[str] = "/get_institutions"
    get_single_end_point: ClassVar[str] = "get_institution"
    add_endpoint: ClassVar[str] = "/add_institution"
    delete_endpoint: ClassVar[str] = "/delete_institution"
    edit_endpoint: ClassVar[str] = "/edit_institution"
    db_table_name: ClassVar[str] = "Institutions"

    @property
    def id(self) -> Optional[int]:
        return self.InstitutionId

    InstitutionId: Optional[int] = bm.ID_FIELD
    InstitutionName: str
    StartingHour: str
    EndingHour: str
    HasBreaks: Literal[0, 1]
    NormalBreakLength: Optional[int] = None
    NormalLessonLength: Optional[int] = None

    def subjects_taught_in_inst(self) -> "Iterator[models.subject.Subject]":
        import models.subject
        yield from models.subject.Subject.from_endpoint(self)

    def terms_in_inst(self) -> "Iterator[models.Term.Term]":
        import models.Term
        yield from models.Term.Term.from_endpoint(self)

    def term_plans_in_inst(self):
        yield from itertools.chain(*[t.plans_in_term() for t in self.terms_in_inst()])


convs_registry.from_json_conv.register_structure_hook(
    cl=Institution,
    func=lambda inst_id, type: Institution.from_end_point_by_id(inst_id)
)
