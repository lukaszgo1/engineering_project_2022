import operator
from typing import (
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class AddClassDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj Klasę"
    affirmative_btn_label: str = "Dodaj"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            label="Identyfikator klasy:",
            identifier="ClassIdentifier"
        ),
    )


class ClassesListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj nową klasę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Nazwa",
            width=400,
            value_getter=operator.attrgetter("ClassIdentifier")
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
    frontend.gui_controls_spec.MenuItemSpec(
        name="Powiąż z podstawą programową",
        on_activate_listener_name="associate_with_term_plan",
        should_show=lambda p: not bool(p.focused_entity.assigned_term_plan)
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        name="Usuń powiązanie z podstawą programową",
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
