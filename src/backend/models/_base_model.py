from typing import (
    ClassVar,
    Dict,
    Final,
    Optional,
    Tuple,
)

import attrs

import backend.app_constants

USER_PRESENTABLE_FIELD_NAME: Final[str] = "userPresentable"


@attrs.define(kw_only=True)
class _BaseModel:

    # `None` signifies that the record has not been inserted yet.
    id: Optional[int] = attrs.field(
        default=None, metadata={USER_PRESENTABLE_FIELD_NAME: False}
    )

    db_table_name: ClassVar[str]
    id_column_name: ClassVar[str]

    @staticmethod
    def is_user_presentable(field) -> bool:
        return field.metadata.get(USER_PRESENTABLE_FIELD_NAME, True)

    @classmethod
    def user_presentable_fields(cls) -> Tuple[str, ...]:
        return tuple(
            _.name for _ in attrs.fields(cls) if cls.is_user_presentable(_)
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
            {_: _ for _ in fields_to_select if _ != cls.id_column_name}
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
        return attrs.asdict(
            inst=self,
            filter=lambda attr, val: self.is_user_presentable(attr)
        )

    def cols_for_insert(self) -> Dict:
        return self.cols_to_attrs()

    def insert_into_db(self) -> None:
        if self.id is not None:
            raise RuntimeError("Model is already in the database.")
        current_instance_vars = self.cols_for_insert()
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
            condition_values=(str(self.id),)
        )
        # Update the instance fields only after
        # the record was correctly updated in the data base.
        for col_name, col_value in new_values.items():
            setattr(self, col_name, col_value)

    def delete_db_record(self) -> None:
        backend.app_constants.active_db_con.delete_record(
            table_name=self.db_table_name,
            condition_string=f"{self.id_column_name} = ?",
            seq=(str(self.id),)
        )


@attrs.define(kw_only=True)
class _Owned_model(_BaseModel):

    owner: _BaseModel = attrs.field(
        metadata={
            USER_PRESENTABLE_FIELD_NAME: False, "should_return_as_id": True
        }
    )
    owner_col_id_name: ClassVar[str]

    def cols_for_insert(self) -> Dict:
        res = super().cols_for_insert()
        res[self.owner_col_id_name] = self.owner.id
        return res
