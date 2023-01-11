import operator
from typing import (
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddTermPlanDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj plan semestralny"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Nazwa:",
            identifier="TermPlanName"
        ),
    )


class TermPlanListing(views._base_views.BaseEntityList):

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj nowy plan semestralny",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("TermPlanName")
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
        name="Wpisy w podstawie",
        on_activate_listener_name="on_show_plan_entries",
    ),
    gui_controls_spec.MenuItemSpec(
        name="Przenieś podstawę do semestru",
        on_activate_listener_name="on_move_term_plan",
    ),
)


class EditTermPlanDlg(AddTermPlanDlg):

    title: str = "Edytuj plan semestralny"
    affirmative_btn_label: str = "Zapisz zmiany"


class MoveTermPlanDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Przenieś podstawę"
    affirmative_btn_label: str = "Przenieś"

    control_specs = (
        gui_controls_spec.LabeledEditFieldSpec(
            identifier="new_plan_name",
            label="Nazwa nowej podstawy:"
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            identifier="target_term",
            label="Docelowy semestr"
        ),
    )


add = AddTermPlanDlg
listing = TermPlanListing
context_menu_spec = items_list
edit = EditTermPlanDlg
