import abc
import dataclasses

from typing import (
    List,
)

import backend.app_constants

NOT_YET_INSERTED = object()


class _BaseModel(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def db_table_name(self) -> str:
        """Return the name of the database table backing up this model."""

    @classmethod
    def all_db_columns(cls) -> List[str]:
        return [f.name for f in dataclasses.fields(cls)]

    @classmethod
    def excluded_fields(cls):
        return set(("id",))

    @classmethod
    def from_db(cls):
        fields_to_select = (cls.id_column_name,)
        fields_to_select += tuple(
            _ for _ in cls.all_db_columns() if _ not in cls.excluded_fields()
        )
        records_in_db = backend.app_constants.active_db_con.fetch_all(
            col_names=fields_to_select,
            table_name=cls.db_table_name
        )
        constructor_fields = {"id": cls.id_column_name}
        constructor_fields.update(
            {_: _ for _ in fields_to_select if _ not in cls.id_column_name}
        )
        for record in records_in_db:
            kwargs_with_vals = dict(
                zip(
                    constructor_fields.keys(),
                    tuple(record[key] for key in constructor_fields.values())
                )
            )
            yield cls(**kwargs_with_vals)
