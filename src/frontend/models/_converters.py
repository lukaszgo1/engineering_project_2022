from typing import (
    Any,
)

import attrs
import cattrs

import models._constants as constants


DEFAULT_CONV = cattrs.Converter(forbid_extra_keys=True)

from_json_conv = DEFAULT_CONV.copy()


def _is_convertable_toid(typ: type[Any]) -> bool:
    return hasattr(typ, "id")


def _unstruct_to_id(val: Any) -> Any:
    return val.id


def create_unstructuring_converters(decorated_cls):
    try:
        cls_fields = attrs.fields(decorated_cls)
    except attrs.exceptions.NotAnAttrsClassError:
        # Since failure in a class decorator is pretty serious just return the class unchanged.
        #  Ideally the exception should be logged,
        # but we don't, and probably won't have logging...
        return decorated_cls
    fields_to_drop = set()
    to_json_converter = cattrs.Converter()
    # When we would be posting this to an actual JSON backend
    # consider using the cattrs converter preconfigured for JSON.
    for field  in cls_fields:
        if field.metadata.get(constants.FieldSpecifiers.ID_COLUMN, False):
            fields_to_drop.add(field.name)
        elif(
            _is_convertable_toid(field.type)
            or (  # Special handling for unions
                hasattr(field.type, "__args__")
                and all(_is_convertable_toid(_) for _ in field.type.__args__)
            )
        ):
            to_json_converter.register_unstructure_hook(field.type, _unstruct_to_id)
    omitters = {_: cattrs.gen.override(omit=True) for _ in fields_to_drop}
    primary_key_omit_hook = cattrs.gen.make_dict_unstructure_fn(
        decorated_cls,
        to_json_converter,
        **omitters
    )
    to_json_converter.register_unstructure_hook(decorated_cls, primary_key_omit_hook)
    decorated_cls.to_json_converter = to_json_converter
    return decorated_cls
