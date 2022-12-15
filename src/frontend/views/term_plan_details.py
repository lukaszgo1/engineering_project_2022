import enum
import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class PossibleDistance(enum.IntEnum):

    DAYS = 0
    WEEKS = 1

    @property
    def label(self) -> str:
        if self == PossibleDistance.DAYS:
            return "dni"
        return "tygodni"


class NonApplicableDistanceCtsDisabler(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_distance_changed)

    def on_distance_changed(self, new_distance):
        new_days_distance_state = new_distance == PossibleDistance.DAYS
        new_weeks_distance_state = new_distance == PossibleDistance.WEEKS
        for control in self._controls_to_modify:
            if control.identifier == "PreferredDistanceInDays":
                control.set_state(new_days_distance_state)
            elif control.identifier == "PreferredDistanceInWeeks":
                control.set_state(new_weeks_distance_state)


class AddTermPlanDetailDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj wpis do podstawy"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Przedmiot:",
            identifier="SubjectId"
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            label="Ilość godzin lekcyjnych:",
            identifier="LessonsAmount"
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            identifier="MinBlockSize",
            label="Minimalna ilość w bloku:"
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            label="Maks ilość w bloku:",
            identifier="MaxBlockSize"
        ),
        frontend.gui_controls_spec.RadioButtonspec(
            label="Co:",
            choices=list(PossibleDistance),
            identifier="DistanceIn",
            on_change_notifier=NonApplicableDistanceCtsDisabler
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            label="Co ile dni:",
            identifier="PreferredDistanceInDays",
            max_val=4,
            should_react_to_changes=True
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            label="Co ile tygodni:",
            identifier="PreferredDistanceInWeeks",
            should_react_to_changes=True
        ),
    )

    def get_values(self) -> dict:
        res = super().get_values()
        distance = res.pop("DistanceIn")
        # The condition below is counter intiutive
        # and deserves additional explanation.
        # We want to make sure that whatever distance is not chosen at present
        # would be set to `None` in the database.
        if distance == PossibleDistance.DAYS:
            res["PreferredDistanceInWeeks"] = None
        elif distance == PossibleDistance.WEEKS:
            res["PreferredDistanceInDays"] = None
        return res


def _to_string_if_not_none(val_to_convert):
    if val_to_convert is not None:
        return str(val_to_convert)
    return ""


class TermPlanDetailsListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj nowy wpis do podstawy",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa przedmiotu",
            width=400,
            value_getter=operator.attrgetter("SubjectId"),
            value_converter=str
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Ilość lekcji",
            width=100,
            value_getter=operator.attrgetter("LessonsAmount"),
            value_converter=str
        ),  
        frontend                .gui_controls_spec.WXListColumnSpec(
            header_name="Min ilość w bloku",
            width=100,
            value_getter    =operator.attrgetter("MinBlockSize"),
            value_converter=str
        ),
        frontend                .gui_controls_spec.WXListColumnSpec(
            header_name="Maks ilość w bloku",
            width=100,
            value_getter    =operator.attrgetter("MaxBlockSize"),
            value_converter=str
        ),
        frontend                .gui_controls_spec.WXListColumnSpec(
            header_name="Co ile dni",
            width=100,  
            value_getter    =operator.attrgetter("PreferredDistanceInDays"),
            value_converter=_to_string_if_not_none
        ),
        frontend                .gui_controls_spec.WXListColumnSpec(
            header_name="Co ile tygodni",
            width=100,  
            value_getter    =operator.attrgetter("PreferredDistanceInWeeks"),
            value_converter=_to_string_if_not_none
        ),
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


class EditTermPlanDetailDlg(AddTermPlanDetailDlg):

    title: str = "Edytuj wpis w podstawie"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddTermPlanDetailDlg
listing = TermPlanDetailsListing
context_menu_spec = items_list
edit = EditTermPlanDetailDlg
