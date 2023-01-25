import operator
from typing import (
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddSubjectDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj przedmiot"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwa przedmiotu:",
            identifier="SubjectName"
        ),
    )


class SubjectsListing(views._base_views.BaseEntityList):

    buttons_in_view: List[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj nowy przedmiot",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("SubjectName")
        )
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
)


class EditSubjectDlg(AddSubjectDlg):

    title: str = "Edytuj zajęcia"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddSubjectDlg
listing = SubjectsListing
context_menu_spec = items_list
edit = EditSubjectDlg
