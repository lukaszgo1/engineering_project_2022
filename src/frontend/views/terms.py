import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class AddTermDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj semestr"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwa:",
            identifier="TermName"
        ),
        frontend.gui_controls_spec.DatePickerSpec(
            label="Data rozpoczęcia:",
            identifier="StartDate",
        ),
        frontend.gui_controls_spec.DatePickerSpec(
            label="Data końca:",
            identifier="EndDate"
        ),
    )


class TermsListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj semestr",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("TermName")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Data rozpoczęcia",
            width=400,
            value_getter=operator.attrgetter("StartDate"),
            value_converter=lambda val: val.strftime("%Y-%m-%d")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Data końca",
            width=400,
            value_getter=operator.attrgetter("EndDate"),
            value_converter=lambda val: val.strftime("%Y-%m-%d")
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


class EditTermDlg(AddTermDlg):

    title: str = "Edytuj semestr"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddTermDlg
listing = TermsListing
context_menu_spec = items_list
edit = EditTermDlg
