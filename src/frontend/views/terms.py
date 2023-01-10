import operator
from typing import (
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddTermDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj semestr"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwa:",
            identifier="TermName"
        ),
        gui_controls_spec.DatePickerSpec(
            label="Data rozpoczęcia:",
            identifier="StartDate",
        ),
        gui_controls_spec.DatePickerSpec(
            label="Data końca:",
            identifier="EndDate"
        ),
    )


class TermsListing(views._base_views.BaseEntityList):

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj semestr",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("TermName")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Data rozpoczęcia",
            width=400,
            value_getter=operator.attrgetter("StartDate"),
            value_converter=lambda val: val.strftime("%Y-%m-%d")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Data końca",
            width=400,
            value_getter=operator.attrgetter("EndDate"),
            value_converter=lambda val: val.strftime("%Y-%m-%d")
        ),
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
    gui_controls_spec.MenuItemSpec(
        name="Podstawy programowe w semestrze",
        on_activate_listener_name="on_show_term_plans"
    ),
    gui_controls_spec.MenuItemSpec(
        name="Dodaj zajęcia do grafiku",
        on_activate_listener_name="on_add_new_schedule_entry"
    ),
)


class EditTermDlg(AddTermDlg):

    title: str = "Edytuj semestr"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddTermDlg
listing = TermsListing
context_menu_spec = items_list
edit = EditTermDlg
