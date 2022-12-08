import operator
from typing import (
    Dict,
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class AddClassRoomDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj salę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            label="Numer:",
            identifier="ClassRoomIdentifier"
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Główny przedmiot:",
            identifier="PrimaryCourse"
        ),
    )

    def get_values(self) -> Dict:
        res = super().get_values()
        res["MainSubjectId"] = res["PrimaryCourse"].id
        return res


class ClassRoomsListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj salę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Numer",
            width=400,
            value_getter=operator.attrgetter("ClassRoomIdentifier")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Główny kurs",
            width=400,
            value_getter=operator.attrgetter("PrimaryCourse"),
            value_converter=str
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


class EditClassDlg(AddClassRoomDlg):

    title: str = "Edytuj salę lekcyjną"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddClassRoomDlg
listing = ClassRoomsListing
context_menu_spec = items_list
edit = EditClassDlg
