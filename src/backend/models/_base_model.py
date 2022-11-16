import abc
import dataclasses

from typing import (
    Dict,
    List,
    Tuple,
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
    def user_presentable_fields(cls) -> Tuple[str, ...]:
        return tuple(
            _ for _ in cls.all_db_columns() if _ not in cls.excluded_fields()
        )

    @classmethod
    def from_db(cls):
        fields_to_select = (cls.id_column_name,)
        fields_to_select += cls.user_presentable_fields()
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

    def cols_to_attrs(self):
        return {
            col_name: getattr(self, col_name) for col_name in self.user_presentable_fields()
        }

    def insert_into_db(self) -> None:
        if self.id is not NOT_YET_INSERTED:
            raise RuntimeError("Model is already in the database.")
        current_instance_vars = self.cols_to_attrs()
        self.id = backend.app_constants.active_db_con.insert(
            table_name=self.db_table_name,
            col_names=tuple(current_instance_vars.keys()),
            col_values=tuple(current_instance_vars.values())
        )

    def update_db_record(self, new_values: Dict) -> None:
        backend.app_constants.active_db_con.update_record(
            table_name=self.db_table_name,
            col_names=tuple(new_values.keys()),
            col_values=tuple(new_values.values()),
            condition_str=f"{self.id_column_name} = ?",
            condition_values=(self.id,)
        )
        # Update the instance fields only after
        # the record was correctly updated in the data base.
        for col_name, col_value in new_values.items():
            setattr(self, col_name, col_value)

    def delete_db_record(self) -> None:
        backend.app_constants.active_db_con.delete_record(
            table_name=self.db_table_name,
            condition_string=f"{self.id_column_name} = ?",
            seq=(self.id,)
        )
