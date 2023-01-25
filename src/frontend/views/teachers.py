import operator
from typing import (
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddTeacherDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj nauczyciela"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Imię:",
            identifier="FirstName"
        ),
        gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwisko:",
            identifier="LastName",
        ),
        gui_controls_spec.CheckBoxSpec(
            label="Dostępny",
            identifier="IsAvailable"
        ),
    )


class TeachersListing(views._base_views.BaseEntityList):

    buttons_in_view: List[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj nauczyciela",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Imię",
            width=400,
            value_getter=operator.attrgetter("FirstName")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Nazwisko",
            width=400,
            value_getter=operator.attrgetter("LastName")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Status",
            width=100,
            value_getter=operator.attrgetter("IsAvailable"),
            value_converter=lambda val: "dostępny" if val else "niedostępny"
        ),
    ]


items_list: Tuple[gui_controls_spec.MenuItemSpec, ...] = (
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
    gui_controls_spec.MenuItemSpec(
        name="Przypisz do przedmiotu",
        on_activate_listener_name="on_assign_to_subject"
    ),
    gui_controls_spec.MenuItemSpec(
        name="Usuń przypisanie do przedmiotu",
        on_activate_listener_name="on_remove_subject_assignment"
    ),
)


class EditTeacherDlg(AddTeacherDlg):

    title: str = "Edytuj nauczyciela"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddTeacherDlg
listing = TeachersListing
context_menu_spec = items_list
edit = EditTeacherDlg
