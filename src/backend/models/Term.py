import datetime
import email.utils
from typing import (
    ClassVar,
    Iterator,
)

import attrs

import backend.models._base_model as bm
import backend.models.TermPlan


def _http_date_to_py_date(date_str: str) -> datetime.date:
    """Convert the date in a HTTP format as returned by
    `flask.jsonify` to a Python date object.
    """
    date_tpl = email.utils.parsedate(date_str)
    year, month, day, *_rest  = date_tpl
    return datetime.date(year, month, day)


@attrs.define(kw_only=True)
class Term(bm._Owned_model):

    get_endpoint: ClassVar[str] = "/get_terms"
    db_table_name: ClassVar[str] = "Terms"
    id_column_name: ClassVar[str] = "TermId"
    owner_col_id_name: ClassVar[str] = "TermInInst"
    StartDate: datetime.date
    EndDate: datetime.date
    TermName: str

    @classmethod
    def initializer_params(cls, db_record: dict) -> dict:
        res =  super().initializer_params(db_record)
        res["StartDate"] = _http_date_to_py_date(res["StartDate"])
        res["EndDate"] = _http_date_to_py_date(res["EndDate"])
        return res

    def plans_in_term(self) -> Iterator[backend.models.TermPlan.TermPlan]:
        yield from backend.models.TermPlan.TermPlan.from_db(self)

    def __str__(self) -> str:
        return self.TermName
