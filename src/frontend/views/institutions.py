import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


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
            has_dependent_controls=True
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="NormalBreakLength",
            label="Długość przerwy:",
            listeners_to_register=["set_state"]
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="NormalLessonLength",
            label="Długość zajęć:",
            listeners_to_register=["set_state"]
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
        name="Dodaj długą przerwę",
        on_activate_listener_name="on_add_break",
        should_show=lambda presenter: presenter.focused_entity.HasBreaks
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

    buttons_in_view: List[
            frontend.gui_controls_spec.WXButtonSpec
    ] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label='Dodaj nową instytucję',
            on_press=lambda evt: evt.EventObject.Parent.presenter.add_new_entry()
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
