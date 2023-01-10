import operator
from typing import (
    Dict,
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddClassRoomDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj salę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Numer:",
            identifier="ClassRoomIdentifier"
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Główny przedmiot:",
            identifier="PrimaryCourse"
        ),
    )


class ClassRoomsListing(views._base_views.BaseEntityList):

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj salę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Numer",
            width=400,
            value_getter=operator.attrgetter("ClassRoomIdentifier")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Główny kurs",
            width=400,
            value_getter=operator.attrgetter("PrimaryCourse"),
            value_converter=str
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


class EditClassDlg(AddClassRoomDlg):

    title: str = "Edytuj salę lekcyjną"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddClassRoomDlg
listing = ClassRoomsListing
context_menu_spec = items_list
edit = EditClassDlg
