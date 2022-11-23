import abc
from typing import (
    Any,
    Callable,
    ClassVar,
    List,
    Optional,
    Union,
    Type,
)

import attrs
import wx

import frontend.gui_control_factories as control_factories


@ attrs.define(frozen=True)
class WXButtonSpec:
    label: str
    on_press: Callable[[wx.CommandEvent], None]


@attrs.define(frozen=True)
class WXListColumnSpec:
    header_name: str
    width: int
    value_getter: Callable[[Any], Optional[Union[str, int]]]
    value_converter: Optional[
        Callable[[Optional[Union[str, int]]], str]
    ] = None


@attrs.define(kw_only=True)
class _ControlWrapperBase(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def _factory_cls(self) -> Type[control_factories._base_control]:
        """Return the factory which creates the wrapper for the control."""

    identifier: str
    has_dependent_controls: bool = False
    listeners_to_register: List[str] = attrs.Factory(list)

    def create(
        self,
        parent: wx.Window
    ) -> control_factories._base_control:
        return self._factory_cls(parent, self)


@attrs.define(kw_only=True)
class LabeledEditFieldSpec(_ControlWrapperBase):

    label: str
    _factory_cls: ClassVar[
        Type[control_factories.labeled_edit_field_factory]
    ] = control_factories.labeled_edit_field_factory


@attrs.define(kw_only=True)
class CheckBoxSpec(_ControlWrapperBase):

    label: str
    _factory_cls: ClassVar[
        Type[control_factories.checkbox_wrapper]
    ] = control_factories.checkbox_wrapper


@attrs.define(kw_only=True)
class MenuItemSpec:

    name: str
    id: int = wx.ID_ANY
    on_activate_listener_name: str
    should_show: Optional[
        Callable[..., bool]
    ] = None

    def create(self, parent_menu: wx.Menu) -> wx.MenuItem:
        return parent_menu.Append(self.id, item=self.name)
