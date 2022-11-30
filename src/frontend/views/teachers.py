import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class AddTeacherDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj nauczyciela"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            label="Imię:",
            identifier="FirstName"
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwisko:",
            identifier="LastName",
        ),
        frontend.gui_controls_spec.CheckBoxSpec(
            label="Dostępny",
            identifier="IsAvailable"
        ),
    )


class TeachersListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj nauczyciela",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Imię",
            width=400,
            value_getter=operator.attrgetter("FirstName")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Nazwisko",
            width=400,
            value_getter=operator.attrgetter("LastName")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Status",
            width=100,
            value_getter=operator.attrgetter("IsAvailable"),
            value_converter=lambda val: "dostępny" if val else "niedostępny"
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


class EditTeacherDlg(AddTeacherDlg):

    title: str = "Edytuj nauczyciela"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddTeacherDlg
listing = TeachersListing
context_menu_spec = items_list
edit = EditTeacherDlg
