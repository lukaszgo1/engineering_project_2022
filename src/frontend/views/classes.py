import operator
from typing import (
    List,
    Tuple,
)

import wx

import gui_controls_spec
import views._base_views


class AddClassDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj Klasę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledEditFieldSpec(
            label="Identyfikator klasy:",
            identifier="ClassIdentifier"
        ),
    )


class ClassesListing(views._base_views.BaseEntityList):

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj nową klasę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("ClassIdentifier")
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
    gui_controls_spec.MenuItemSpec(
        name="Powiąż z planem semestralnym",
        on_activate_listener_name="associate_with_term_plan",
        should_show=lambda p: not bool(p.focused_entity.assigned_term_plan)
    ),
    gui_controls_spec.MenuItemSpec(
        name="Usuń powiązanie z planem semestralnym",
        on_activate_listener_name="remove_association_with_term_plan",
        should_show=lambda p: bool(p.focused_entity.assigned_term_plan)
    ),
)


class EditClassDlg(AddClassDlg):

    title: str = "Edytuj klasę"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddClassDlg
listing = ClassesListing
context_menu_spec = items_list
edit = EditClassDlg
