"""Contains factories creating various controls from the WX Python library.

Note that since some of these factories are classes and some are functions
to have a consistent namimg we are going to just use Snake case
for all the factories.
"""

from __future__ import annotations

import abc
import datetime

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Sequence,
    TYPE_CHECKING,
)

import wx
import wx.adv

if TYPE_CHECKING:
    import gui_controls_spec as ctrl_specs


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
        self._registered_listeners: List[Callable[..., None]] = []

    def register_to_changes(self, on_change_event) -> None:
        self._registered_listeners.append(on_change_event)

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


class spin_control_factory(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.SpinControlSpec"
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
        self._spin_control = wx.SpinCtrl(ctrl_parent)
        self._sizer.Add(self._spin_control)
        self._spin_control.SetIncrement(control_params.increment)
        self._spin_control.Min = control_params.min_val
        if control_params.max_val is not None:
            self._spin_control.Max = control_params.max_val

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._sizer)

    @property
    def value(self) -> int:
        return self._spin_control.Value

    def get_value(self) -> Dict[str, int]:
        return {self.identifier: self.value}

    def set_value(self, new_val: int) -> None:
        if new_val is not None:
            self._spin_control.Value = new_val

    def set_state(self, new_state: bool) -> None:
        self._spin_control.Enable(new_state)
        self._label.Enable(new_state)
        self.is_enabled = new_state


class radio_button_factory(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.RadioButtonspec"
    ) -> None:
        super().__init__(ctrl_parent, control_params)
        self._rb_raw_vals = control_params.choices
        self.rb_values = [_.label for _ in control_params.choices]
        self._radio_button = wx.RadioBox(
            ctrl_parent,
            label=control_params.label,
            choices=self.rb_values,
            style=wx.RA_SPECIFY_ROWS
        )
        self._radio_button.Bind(wx.EVT_RADIOBOX, self.on_value_change)

    def notify_listeners(self, new_val):
        for listener in self._registered_listeners:
            listener(new_val)

    def on_value_change(self, event):
        new_val = list(self._rb_raw_vals)[self._radio_button.Selection]
        self.notify_listeners(new_val)

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._radio_button)

    @property
    def value(self):
        return list(self._rb_raw_vals)[self._radio_button.Selection]

    def get_value(self) -> Dict[str, Any]:
        return {self.identifier: self.value}

    def set_value(self, new_val: Any) -> None:
        entry_index = list(self._rb_raw_vals).index(new_val)
        self._radio_button.Selection = entry_index
        self.notify_listeners(new_val)


class labeled_combo_box_factory(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.LabeledComboBoxSpec"
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
        self._combobox = wx.Choice(ctrl_parent)
        self._sizer.Add(self._combobox)
        self._combobox.Bind(wx.EVT_CHOICE, self.on_choice)
        self._parent = ctrl_parent

    def notify_when_state_changed(self):
        new_val = self.value
        for listener in self._registered_listeners:
            listener(new_val)

    def on_choice(self, event):
        self.notify_when_state_changed()

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._sizer)

    def set_value(self, new_val: "ctrl_specs.ComboBoxvaluesSpec") -> None:
        self._indexes_to_vals = {k: v for k, v in enumerate(new_val.values)}
        self._combobox.Set([str(_) for _ in self._indexes_to_vals.values()])
        if new_val.initial_selection is not None:
            self._combobox.SetSelection(new_val.initial_selection)
            self.notify_when_state_changed()
        self._combobox.InvalidateBestSize()
        self._combobox.SetSize(self._combobox.GetBestSize())
        self._parent.Layout()
        self._parent.Fit()

    @property
    def value(self):
        cb_selected_index = self._combobox.Selection
        if cb_selected_index is wx.NOT_FOUND:
            return None
        return self._indexes_to_vals[cb_selected_index]

    def get_value(self) -> Dict[str, Any]:
        return {self.identifier: self.value}


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
        self._edit = wx.TextCtrl(ctrl_parent, size=(250, 20))
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

    @property
    def value(self):
        return self._edit.GetValue()

    def get_value(self) -> Dict[str, str]:
        return {self.identifier: self.value}


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

    @property
    def value(self):
        return self._chk.IsChecked()

    def get_value(self) -> Dict[str, bool]:
        return {self.identifier: self.value}


class date_picker_factory(_base_control):

    def __init__(
        self,
        ctrl_parent: wx.Window,
        control_params: "ctrl_specs.DatePickerSpec"
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
        self._picker = wx.adv.DatePickerCtrl(ctrl_parent)
        self._sizer.Add(self._picker)

    def add_to_sizer(self, parent_sizer: wx.Sizer) -> None:
        parent_sizer.Add(self._sizer)

    def set_value(self, new_val: Any) -> None:
        self._picker.Value = wx.DateTime(new_val)

    @property
    def value(self):
        control_val = self._picker.Value
        year = control_val.year
        month = control_val.month + 1  # Month's in  WX are numbered from 0
        day = control_val.day
        return datetime.date(year=year, month=month, day=day)

    def get_value(self) -> Dict[str, Any]:
        return {self.identifier: self.value}


def wx_context_menu_factory(
        item_specs: Sequence["ctrl_specs.MenuItemSpec"],
        on_click_listeners: Sequence[Callable[[wx.ContextMenuEvent], None]]
) -> wx.Menu:
    menu_obj = wx.Menu()
    for item_spec, listener in zip(item_specs, on_click_listeners):
        menu_item = item_spec.create(menu_obj)
        menu_obj.Bind(wx.EVT_MENU, listener, menu_item)
    return menu_obj
