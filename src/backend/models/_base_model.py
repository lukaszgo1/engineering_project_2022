from typing import (
    ClassVar,
    Dict,
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
import cattrs

import backend.app_constants
import backend.models._converters as convs_registry
import frontend.api_utils
import backend.models._constants as constants


class NonExistingEntityRequested(Exception):

    """Raised when the entity with the given id does not exist in db."""


ID_FIELD = attrs.field(
        default=None,
        metadata={constants.FieldSpecifiers.ID_COLUMN: True},
)
main_fk_field = attrs.field(metadata={constants.FieldSpecifiers.MAIN_FK_COLUMN: True})


@attrs.define(kw_only=True)
class _BaseModel:

    # This is present only for type annotations and auto complete in id's.
    # The actual converter instance
    # is added dynamically by the decorator at runtime.
    to_json_converter: ClassVar[cattrs.Converter]

    @classmethod
    def id_field_name(cls):
        return cls.field_name_for_truthy_metadata(constants.FieldSpecifiers.ID_COLUMN)

    @classmethod
    def field_name_for_truthy_metadata(cls, metadata_key: constants.FieldSpecifiers) -> str:
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

    def set_id(self, new_val: Optional[int]) -> None:
        setattr(
            self,
            self.field_name_for_truthy_metadata(constants.FieldSpecifiers.ID_COLUMN),
            new_val
        )

    db_table_name: ClassVar[str]
    get_endpoint: ClassVar[str]
    get_single_end_point: ClassVar[str]

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
        return cls(**record)

    def cols_to_attrs(self):

        def should_include(attr, val) -> bool:
            return attr.metadata.get(constants.FieldSpecifiers.ID_COLUMN, True)

        return attrs.asdict(
            inst=self,
            filter=should_include,
            recurse=False
        )

    def cols_for_insert(self) -> Dict:
        res = self.to_json_converter.unstructure(self)
        return res

    def insert_into_db(self) -> None:
        if self.id is not None:
            raise RuntimeError("Model is already in the database.")
        current_instance_vars = self.cols_for_insert()
        self.set_id(backend.app_constants.active_db_con.insert(
            table_name=self.db_table_name,
            col_names=tuple(current_instance_vars.keys()),
            col_values=tuple(current_instance_vars.values())
        ))

    def update_db_record(self, new_values: Dict) -> Self:
        record_with_updated_vals = attrs.evolve(self, **new_values)
        updated_fields = record_with_updated_vals.to_json_converter.unstructure(record_with_updated_vals)
        backend.app_constants.active_db_con.update_record(
            table_name=self.db_table_name,
            col_names=tuple(updated_fields.keys()),
            col_values=tuple(updated_fields.values()),
            condition_str=f"{self.id_field_name()} = ?",
            condition_values=(str(self.id),)
        )
        return record_with_updated_vals

    def delete_db_record(self) -> None:
        backend.app_constants.active_db_con.delete_record(
            table_name=self.db_table_name,
            condition_string=f"{self.id_field_name()} = ?",
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
        return cls.field_name_for_truthy_metadata(constants.FieldSpecifiers.MAIN_FK_COLUMN)

    @owner.setter
    def owner(self, new_val):
        setattr(
            self,
            self.fk_field_name(),
            new_val
        )

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
