import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class RegularLessonsCtrRevealer(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_change_state)

    def on_change_state(self, new_state: bool) -> None:
        for control in self._controls_to_modify:
            control.set_state(new_state)


class AddInst(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj instytucję"
    affirmative_btn_label: str = "Dodaj"

    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="InstitutionName",
            label="Nazwa instytucji:"
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="StartingHour",
            label="Godzina rozpoczęcia zajęć:"
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="EndingHour",
            label="Godzina końca zajęć:"
        ),
        frontend.gui_controls_spec.CheckBoxSpec(
            identifier="HasBreaks",
            label="Czy przerwy",
            on_change_notifier=RegularLessonsCtrRevealer
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            identifier="NormalBreakLength",
            label="Długość przerwy:",
            should_react_to_changes=True,
            increment=5,
            min_val=5,
        ),
        frontend.gui_controls_spec.SpinControlSpec(
            identifier="NormalLessonLength",
            label="Długość zajęć:",
            should_react_to_changes=True,
            increment=5
        ),
    )


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
    frontend.gui_controls_spec.MenuItemSpec(
        name="Długie przerwy",
        on_activate_listener_name="on_show_long_breaks",
        should_show=lambda presenter: presenter.focused_entity.HasBreaks
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        name="Klasy",
        on_activate_listener_name="on_show_classes"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        name="Przedmioty",
        on_activate_listener_name="on_show_subjects"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        name="Nauczyciele",
        on_activate_listener_name="on_show_teachers"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        name="Sale lekcyjne",
        on_activate_listener_name="on_show_class_rooms"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
    name="Semestry",
    on_activate_listener_name="on_show_terms"
    ),
)


class EditInst(AddInst):

    title: str = "Edytuj instytucję"
    affirmative_btn_label: str = "Zapisz zmiany"


def _to_string_if_truthy(val) -> str:
    if val:
        return str(val)
    return ""


class InstitutionsListing(frontend.views._base_views.BaseEntityList):

    is_main_view: bool = True

    buttons_in_view: List[
            frontend.gui_controls_spec.WXButtonSpec
    ] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label='Dodaj nową instytucję',
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Nazwa',
            width=400,
            value_getter=operator.attrgetter("InstitutionName")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Godzina rozpoczęcia zajęć',
            width=200,
            value_getter=operator.attrgetter("StartingHour")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Godzina zakończenia zajęć',
            width=200,
            value_getter=operator.attrgetter("EndingHour")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Czy przerwy',
            width=150,
            value_getter=operator.attrgetter("HasBreaks"),
            value_converter=lambda val: "Tak" if val else "Nie"
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Długość przerwy',
            width=150,
            value_getter=operator.attrgetter("NormalBreakLength"),
            value_converter=_to_string_if_truthy
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name='Długość zajęć',
            width=150,
            value_getter=operator.attrgetter("NormalLessonLength"),
            value_converter=_to_string_if_truthy
        ),
    ]


listing = InstitutionsListing
add = AddInst
context_menu_spec = items_list
edit = EditInst
