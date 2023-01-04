from __future__ import annotations

import abc
import datetime
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
    value_getter: Callable[[Any], Optional[Union[str, int, datetime.date]]]
    value_converter: Optional[
        Callable[[Optional[Union[str, int, datetime.date]]], str]
    ] = None


class OnChangeListener:

    def __init__(self, presenter, emitting_control) -> None:
        self._presenter = presenter
        self._emitting_control = emitting_control
        self._controls_to_modify = list()

    def add_dependend_control(self, control: _ControlWrapperBase):
        self._controls_to_modify.append(control)

    def registered_control_by_identifier(self, identifier: str):
        matching_controls = [
            _ for _ in self._controls_to_modify
            if _.identifier == identifier
        ]
        if len(matching_controls) > 1:
            raise RuntimeError("Multiple controls with the same identifier were registered")
        return matching_controls[0]


class ComboBoxvaluesSpec:

    """Define interface for values passed to wrapper around `wx.Choice`"""

    def __init__(
        self,
        values: List[Any],
        initial_selection: Optional[int] = None
    ) -> None:
        self.values = values
        self.initial_selection = initial_selection


@attrs.define(kw_only=True)
class _ControlWrapperBase(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def _factory_cls(self) -> Type[control_factories._base_control]:
        """Return the factory which creates the wrapper for the control."""

    identifier: str
    on_change_notifier: Optional[Type[OnChangeListener]] = None
    should_react_to_changes: bool = False

    def create(
        self,
        parent: wx.Window
    ) -> control_factories._base_control:
        return self._factory_cls(parent, self)


@attrs.define(kw_only=True)
class SpinControlSpec(_ControlWrapperBase):

    label: str
    min_val: int = 1
    max_val: Optional[int] = None
    increment: int = 1
    _factory_cls: ClassVar[
        Type[control_factories.spin_control_factory]
    ] = control_factories.spin_control_factory


@attrs.define(kw_only=True)
class RadioButtonspec(_ControlWrapperBase):

    label: str
    choices: Any
    _factory_cls: ClassVar[
        type[control_factories.radio_button_factory]
    ] = control_factories.radio_button_factory


@attrs.define(kw_only=True)
class LabeledEditFieldSpec(_ControlWrapperBase):

    label: str
    _factory_cls: ClassVar[
        Type[control_factories.labeled_edit_field_factory]
    ] = control_factories.labeled_edit_field_factory


@attrs.define(kw_only=True)
class LabeledComboBoxSpec(_ControlWrapperBase):

    label: str
    _factory_cls: ClassVar[
        Type[control_factories.labeled_combo_box_factory]
    ] = control_factories.labeled_combo_box_factory


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


class ToolBarItemSpec:

    _IDS_TO_ICONS: ClassVar[dict[int, str]] = {
        wx.ID_DELETE: wx.ART_DELETE,
        wx.ID_EDIT: wx.ART_EDIT,
    }
    last_used_id: ClassVar[int] = 0
    DEFAULT_BITMAP_TYPE = wx.ART_LIST_VIEW
    _state: bool = True

    def __init__(self, obj_spec: MenuItemSpec, on_click) -> None:
        self._obj_spec = obj_spec
        self._on_click = on_click
        self._item_id = None
        self._parent_tooolbar: Optional[wx.ToolBar] = None

    def _create_toolbar_item_bitmap(self):
        bitmap_to_use = self._IDS_TO_ICONS.get(
            self._obj_spec.id,
            self.DEFAULT_BITMAP_TYPE
        )
        return wx.ArtProvider().GetBitmap(bitmap_to_use, wx.ART_TOOLBAR)

    @property
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, new_state: bool) -> None:
        if new_state != self.state:
            self._parent_tooolbar.EnableTool(self.item_id, new_state)
            self._state = new_state

    def on_reevaluate_state(self, presenter):
        if not presenter.any_focused:
            self.state = False
        else:
            if(
                self._obj_spec.should_show is not None
                and callable(self._obj_spec.should_show)
            ):
                self.state = self._obj_spec.should_show(presenter)
            else:
                self.state = True

    @property
    def  label(self) -> str:
        return self._obj_spec.name

    @property
    def bitmap(self):
        return self._create_toolbar_item_bitmap()

    @property
    def item_id(self) -> int:
        if self._item_id is None:
            self.__class__.last_used_id += 1
            self._item_id = self.__class__.last_used_id
        return self._item_id

    def click(self):
        self._on_click(None)  # TODO: This is ugly

    def set_parent(self, parent_toolbar: wx.ToolBar) -> None:
        self._parent_tooolbar = parent_toolbar


@attrs.define(kw_only=True)
class DatePickerSpec(_ControlWrapperBase):

    label: str
    _factory_cls: ClassVar[
        Type[control_factories.date_picker_factory]
    ] = control_factories.date_picker_factory
