import operator
from typing import (
    Dict,
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class AllowedBreaksProducer(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_length_selected)

    def on_new_length_selected(self, length: int):
        new_breaks = self._presenter.possible_breaks(length)
        for control in self._controls_to_modify:
            control.set_value(new_breaks)


class AddBreakDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj długą przerwę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Długość przerwy:",
            identifier="break_length",
            on_change_notifier=AllowedBreaksProducer
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
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


class BreaksListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj długą przerwę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Początek przerwy",
            width=400,
            value_getter=operator.attrgetter("BreakStartingHour")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Koniec przerwy",
            width=400,
            value_getter=operator.attrgetter("BreakEndingHour")
        )
    ]


items_list: Tuple[frontend.gui_controls_spec.MenuItemSpec, ...] = (
    frontend.gui_controls_spec.MenuItemSpec(
        id=wx.ID_EDIT,
        name="Edytuj",
        on_activate_listener_name="on_edit"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        id=wx.ID_DELETE,
        name="Usuń",
        on_activate_listener_name="on_delete"
    ),
)


add = AddBreakDlg
listing = BreaksListing
context_menu_spec = items_list
