import dataclasses
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)


@dataclasses.dataclass(frozen=True)
class WXButtonSpec:
    label: str
    on_press: Callable[[], None]


@dataclasses.dataclass(frozen=True)
class WXListColumnSpec:
    header_name: str
    width: int
    value_getter: Callable[[Any], Optional[Union[str, int]]]
    value_converter: Optional[
        Callable[[Optional[Union[str, int]]], str]
    ] = None
