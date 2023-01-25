import datetime
import email.utils
from typing import (
    ClassVar,
    Iterator,
    Optional,
    TYPE_CHECKING,
)

import attrs

import models._base_model as bm
import models.institution
if TYPE_CHECKING:
    import models.TermPlan
import models._converters as convs_registry


def _http_date_to_py_date(date_str: str) -> datetime.date:
    """Convert the date in a HTTP format as returned by
    `flask.jsonify` to a Python date object.
    """
    date_tpl = email.utils.parsedate(date_str)
    year, month, day, *_rest  = date_tpl
    return datetime.date(year, month, day)


@convs_registry.create_unstructuring_converters
@attrs.define(kw_only=True)
class Term(bm._Owned_model):

    @property
    def id(self) -> Optional[int]:
        return self.TermId

    get_endpoint: ClassVar[str] = "/get_terms"
    get_single_end_point: ClassVar[str] = "get_term"
    add_endpoint: ClassVar[str] = "/add_term"
    delete_endpoint: ClassVar[str] = "/delete_term"
    edit_endpoint: ClassVar[str] = "/edit_term"
    db_table_name: ClassVar[str] = "Terms"
    TermId: Optional[int] = bm.ID_FIELD
    TermInInst: models.institution.Institution = bm.main_fk_field
    StartDate: datetime.date
    EndDate: datetime.date
    TermName: str

    def plans_in_term(self) -> "Iterator[models.TermPlan.TermPlan]":
        import models.TermPlan
        yield from models.TermPlan.TermPlan.from_endpoint(self)

    def __str__(self) -> str:
        return self.TermName


convs_registry.from_json_conv.register_structure_hook(
    cl=datetime.date,
    func=lambda dt_as_str, type: _http_date_to_py_date(dt_as_str)
)

convs_registry.from_json_conv.register_structure_hook(
    cl=Term,
    func=lambda term_id, type: Term.from_end_point_by_id(term_id)
)
