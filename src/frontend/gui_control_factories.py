"""Contains factories creating various controls from the WX Python library.

Note that since some of these factories are classes and some are functions
to have a consistent namimg we are going to just use Snake case
for all the factories.
"""

from __future__ import annotations

import abc

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Sequence,
    TYPE_CHECKING,
)

import wx

if TYPE_CHECKING:
    import frontend.gui_controls_spec as ctrl_specs


def wx_button_factory(
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.WXButtonSpec"
) -> wx.Button:
    btn = wx.Button(ctrl_parent, label=control_params.label)
    btn.Bind(wx.EVT_BUTTON, control_params.on_press)
    return btn


class _base_control (metaclass=abc.ABCMeta):

    _identifier: str

    @property
    def identifier(self) -> str:
        return self._identifier

    _is_enabled: bool = True

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, val: bool) -> None:
        self._is_enabled = val

    @abc.abstractmethod
    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs._ControlWrapperBase"
    ) -> None:
        """Create our wrapper around WX control.

        The initializer accepts a spec for the control, and the parent window
        to which it should be added.
        """
        self._identifier = control_params.identifier
        self._listener_names = control_params.listeners_to_register
        self._registered_listeners: List[Callable[..., None]] = []

    def register_to_changes(self, subject: _base_control) -> None:
        for on_change_trigger_name in self._listener_names:
            subject._registered_listeners.append(
                getattr(self, on_change_trigger_name)
            )

    @abc.abstractmethod
    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        """Add the underlying WX control to a specified sizer."""

    @abc.abstractmethod
    def set_value(self, new_val: Any) -> None:
        ...

    @abc.abstractmethod
    def get_value(self) -> Dict[str, Any]:
        """Return a dictionary where the keys are identifiers of the control,
        and value is the value of the underlying vidget.
        """


class labeled_edit_field_factory(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.LabeledEditFieldSpec"
    ) -> None:
        super().__init__(ctrl_parent, control_params)
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label = wx.StaticText(
            ctrl_parent,
            label=control_params.label,
            size=(150, -1)
        )
        self._sizer.Add(self._label, flag=wx.ALIGN_CENTER_VERTICAL)
        self._sizer.AddSpacer(10)
        self._edit = wx.TextCtrl(ctrl_parent)
        self._sizer.Add(self._edit)

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._sizer)

    def set_state(self, new_state: bool) -> None:
        self._label.Enable(new_state)
        self._edit.Enable(new_state)
        self.is_enabled = new_state

    def set_value(self, new_val: str) -> None:
        if new_val:
            self._edit.SetValue(str(new_val))

    def get_value(self) -> Dict[str, str]:
        return {self.identifier: self._edit.GetValue()}


class checkbox_wrapper(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.CheckBoxSpec"
    ) -> None:
        super().__init__(ctrl_parent, control_params)
        self._chk = wx.CheckBox(ctrl_parent, label=control_params.label)
        self._chk.Bind(wx.EVT_CHECKBOX, self.on_click)

    def on_click(self, event: wx.CommandEvent) -> None:
        self.notify_when_state_changed(event.IsChecked())

    def notify_when_state_changed(self, new_state: bool) -> None:
        for listener in self._registered_listeners:
            listener(new_state)

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._chk)

    def set_value(self, new_val: bool) -> None:
        self._chk.SetValue(new_val)
        # We don't get a click event when setting value manually,
        # so notify observers ourselves.
        self.notify_when_state_changed(new_val)

    def get_value(self) -> Dict[str, bool]:
        return {self.identifier: self._chk.IsChecked()}


def wx_context_menu_factory(
        item_specs: Sequence["ctrl_specs.MenuItemSpec"],
        on_click_listeners: Sequence[Callable[[wx.ContextMenuEvent], None]]
) -> wx.Menu:
    menu_obj = wx.Menu()
    for item_spec, listener in zip(item_specs, on_click_listeners):
        menu_item = item_spec.create(menu_obj)
        menu_obj.Bind(wx.EVT_MENU, listener, menu_item)
    return menu_obj
