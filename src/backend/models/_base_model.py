from typing import (
    ClassVar,
    Dict,
    Final,
    Optional,
    Tuple,
)
from typing_extensions import (
    Self,  # Python 3.11 adds native support
)

from collections.abc import (
    Iterable,
)

import attrs

import backend.app_constants
import backend.models._converters as convs_registry
import frontend.api_utils


class NonExistingEntityRequested(Exception):

    """Raised when the entity with the given id does not exist in db."""


USER_PRESENTABLE_FIELD_NAME: Final[str] = "userPresentable"


# When / if refactoring consider to use enum.
ID_FIELD_NAME: Final[str] = "is_id_columnt"
MAIN_FK_FIELD_NAME: Final[str] = "main_fk"

ID_FIELD = attrs.field(
        default=None,
        metadata={ID_FIELD_NAME: True},
)
main_fk_field = attrs.field(metadata={MAIN_FK_FIELD_NAME: True})


@attrs.define(kw_only=True)
class _BaseModel:

    @classmethod
    def field_name_for_truthy_metadata(cls, metadata_key: str) -> str:
        for field_name, field_atrs in attrs.fields_dict(cls).items():
            if field_atrs.metadata.get(metadata_key, False):
                return field_name
        else:
            raise RuntimeError(
                (
                    f"Failed to find field with metadata {metadata_key}, "
                    f"for class {cls}"
                )
            )

    @property
    def id(self) -> Optional[int]:
        """Return id of this record.
        If this is returns `None` the record has not been inserted into database yet.
        """

    @id.setter
    def id(self, new_val: Optional[int]) -> None:
        setattr(
            self,
            self.field_name_for_truthy_metadata(ID_FIELD_NAME),
            new_val
        )

    db_table_name: ClassVar[str]
    id_column_name: ClassVar[str]
    get_endpoint: ClassVar[str]
    get_single_end_point: ClassVar[str]

    @staticmethod
    def is_user_presentable(field) -> bool:
        return field.metadata.get(USER_PRESENTABLE_FIELD_NAME, True)

    @staticmethod
    def records_from_end_point(end_point_name):
        yield from frontend.api_utils.get_data(end_point_name)["item"]

    @classmethod
    def from_json_info(cls, json_info) -> Self:
        return convs_registry.from_json_conv.structure_attrs_fromdict(
            json_info, cls
        )

    @classmethod
    def from_endpoint(cls) -> Iterable[Self]:
        for record in cls.records_from_end_point(cls.get_endpoint):
            yield cls.from_json_info(record)

    @classmethod
    def from_end_point_by_id(cls, entity_id: int) -> Self:
        res = frontend.api_utils.get_data(
            cls.get_single_end_point,
            entity_id=str(entity_id)
        )["item"]
        if res is not None:
            return cls.from_json_info(res)
        raise NonExistingEntityRequested

    @classmethod
    def from_normalized_record(cls, record) -> Self:
        return convs_registry.DEFAULT_CONV.structure_attrs_fromdict(
            record, cls
        )

    def cols_to_attrs(self):
        return attrs.asdict(
            inst=self,
            filter=lambda attr, val: self.is_user_presentable(attr),
            recurse=False
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

    @property
    def owner(self) -> _BaseModel:
        """Return the entity representing main foreign key for this model"""
        return getattr(self, self.fk_field_name())

    @classmethod
    def fk_field_name(cls):
        return cls.field_name_for_truthy_metadata(MAIN_FK_FIELD_NAME)

    @owner.setter
    def owner(self, new_val):
        setattr(
            self,
            self.fk_field_name(),
            new_val
        )

    owner_col_id_name: ClassVar[str]

    def cols_for_insert(self) -> Dict:
        res = super().cols_for_insert()
        res[self.owner_col_id_name] = self.owner.id
        return res

    @staticmethod
    def data_from_end_point(end_point_name, end_point_id):
        yield from frontend.api_utils.get_data(
            end_point_name,
            entity_id=end_point_id
        )["item"]

    @classmethod
    def from_endpoint(cls, owner: _BaseModel):
        for record in cls.data_from_end_point(
            end_point_name=cls.get_endpoint,
            end_point_id=str(owner.id)
        ):
            yield cls.from_json_info(record)
