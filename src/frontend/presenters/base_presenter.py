from __future__ import annotations

from typing import (
    Any,
)

import models._base_model
import gui_control_factories
import gui_controls_spec
import presentation_manager


class BasePresenter:

    MODEL_CLASS: type[models._base_model._BaseModel]
    view_collections = Any  # Add type hint
    all_records: list[models._base_model._BaseModel]
    detail_presenters = ()

    def __init__(self) -> None:
        self._initial_selection = 0
        self.is_presenting = False
        self._focused_entity_index = -1
        self.all_records = list()
        self.toolbar_items_in_view = list()
        for spec in self.view_collections.context_menu_spec:
            self.toolbar_items_in_view.append(gui_controls_spec.ToolBarItemSpec(
                obj_spec=spec,
                on_click=self._on_click_handler_factory(spec.on_activate_listener_name)
            ))

    def set_toolbar_icons_state(self):
        for item in self.toolbar_items_in_view:
            item.on_reevaluate_state(self)

    def on_new_item_gained_focus(self, item_index: int) -> None:
        self._focused_entity_index = item_index
        self.set_toolbar_icons_state()

    @property
    def focused_entity(self) -> models._base_model._BaseModel:
        if not self.any_focused:
            raise RuntimeError("No entity has focus")
        return self.all_records[self._focused_entity_index]

    @property
    def any_focused(self) -> bool:
        return self._focused_entity_index >= 0

    def _present_single_in_view(
        self,
        to_show: models._base_model._BaseModel,
        should_focus: bool = False,
    ) -> None:
        self.all_records.append(to_show)
        self.p.add_new_item(
            to_show, should_focus=should_focus
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint()

    def handle_detail_presenter(self, detail_pres):
        raise RuntimeError("Override if applicable")

    def present_all(self, view_pos = 1):
        self.is_presenting = True
        det_press = []
        for det_pres in self.detail_presenters:
            det_press.append(det_pres())
        self.p = self.view_collections.listing(presenter=self, detail_presenters=det_press)
        self.p.on_item_focused_listeners.append(
            self.on_new_item_gained_focus
        )
        self.p.show(view_pos)
        for record in self.get_all_records():
            self._present_single_in_view(record)
        self.p.focus_list(self._initial_selection)
        self.set_toolbar_icons_state()
        for d in det_press:
            self.handle_detail_presenter(d)

    def hide(self):
        if self.is_presenting:
            self._initial_selection = self._focused_entity_index
            self.p.Hide()

    @property
    def initial_vals_for_add(self):
        return dict()

    def create_new_entity_from_user_input(self, entered_vals):
        """Given user input
        attempts to create a complete entity from the model.
        """

    @property
    def new_windows_parent(self):
        if self.is_presenting:
            return self.p
        return presentation_manager.get_presentation_manager().main_window

    def add_new_entry(self):
        add_dlg = self.view_collections.add(
            parent=self.new_windows_parent,
            presenter=self
        )
        add_dlg.set_values(self.initial_vals_for_add)
        with add_dlg as dlg:
            dlg: self.view_collections.add
            if dlg.ShowModal() == dlg.AffirmativeId:
                new_entity = self.create_new_entity_from_user_input(
                    dlg.get_values()
                )
                new_entity.insert_into_db()
                if self.is_presenting:
                    self._present_single_in_view(new_entity, should_focus=True)
                self.set_toolbar_icons_state()

    def _on_click_handler_factory(self, method_name: str):
        return lambda e: getattr(self, method_name)()

    def vals_for_edit(self):
        return self.focused_entity.cols_to_attrs()

    def on_edit(self):
        edit_dlg = self.view_collections.edit(parent=self.p)
        edit_dlg.set_values(self.vals_for_edit())
        with edit_dlg as dlg:
            dlg: self.view_collections.edit
            if dlg.ShowModal() == dlg.AffirmativeId:
                new_values = dlg.get_values()
                self.focused_entity.update_db_record(new_values=new_values)
                self.p.update_shown_entity(
                    self.focused_entity,
                    self._focused_entity_index
                )
                self.set_toolbar_icons_state()

    def show_context_menu_for_entity(self):
        if self.any_focused:
            specs = []
            handlers = []
            for item_spec in self.view_collections.context_menu_spec:
                if (
                    item_spec.should_show is None
                    or not callable(item_spec.should_show)
                    or item_spec.should_show(self)
                ):
                    specs.append(item_spec)
                    handlers.append(self._on_click_handler_factory(
                        item_spec.on_activate_listener_name
                    ))
            menu = gui_control_factories.wx_context_menu_factory(
                item_specs=specs,
                on_click_listeners=handlers
            )
            return menu

    def on_delete(self) -> None:
        index_to_remove = self._focused_entity_index
        self.all_records[index_to_remove].delete_db_record()
        del self.all_records[index_to_remove]
        self.p.delete_item(index_to_remove)

    def show_previous_view(self):
        presentation_manager.get_presentation_manager().show_previous_view_if_any()
