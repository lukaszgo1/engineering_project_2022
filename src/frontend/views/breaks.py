import operator
from typing import (
    Dict,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AllowedBreaksProducer(gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_length_selected)

    def on_new_length_selected(self, length: int):
        new_breaks = list(self._presenter.possible_breaks(length))
        for control in self._controls_to_modify:
            control.set_value(
                gui_controls_spec.ComboBoxvaluesSpec(new_breaks)
            )


class AddBreakDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj długą przerwę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledComboBoxSpec(
            label="Długość przerwy:",
            identifier="break_length",
            on_change_notifier=AllowedBreaksProducer
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Godziny przerwy:",
            identifier="break_time",
            should_react_to_changes=True
        ),
    )

    def get_values(self) -> Dict:
        res = super().get_values()
        selected_break = res["break_time"]
        return {
            "BreakStartingHour": selected_break.start_as_string,
            "BreakEndingHour": selected_break.end_as_string,
        }


class BreaksListing(views._base_views.BaseEntityList):

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj długą przerwę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Początek przerwy",
            width=400,
            value_getter=operator.attrgetter("BreakStartingHour")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Koniec przerwy",
            width=400,
            value_getter=operator.attrgetter("BreakEndingHour")
        )
    ]


items_list: tuple[gui_controls_spec.MenuItemSpec, ...] = (
    gui_controls_spec.MenuItemSpec(
        id=wx.ID_EDIT,
        name="Edytuj",
        on_activate_listener_name="on_edit"
    ),
    gui_controls_spec.MenuItemSpec(
        id=wx.ID_DELETE,
        name="Usuń",
        on_activate_listener_name="on_delete"
    ),
)


add = AddBreakDlg
listing = BreaksListing
context_menu_spec = items_list
