from __future__ import annotations

from typing import (
    List,
)

import wx

import backend.models.institution
import frontend.views.institutions
import frontend.gui_control_factories


class InstitutionPresenter:

    MODEL_CLASS = backend.models.institution.Institution
    view_collections = frontend.views.institutions
    all_records: List[MODEL_CLASS]

    def __init__(
        self,
        tmp_panel: frontend.views.institutions._listing.InstitutionsListing
    ) -> None:
        self._focused_entity_index = -1
        self.p = tmp_panel
        self.all_records = list()
        self.p.on_item_focused_listeners.append(
            self.on_new_item_gained_focus
        )
        self.p.presenter = self

    def on_new_item_gained_focus(self, item_index: int) -> None:
        self._focused_entity_index = item_index

    @property
    def focused_entity(self) -> MODEL_CLASS:
        if not self.any_focused:
            raise RuntimeError("No entity has focus")
        return self.all_records[self._focused_entity_index]

    @property
    def any_focused(self) -> bool:
        return self._focused_entity_index >= 0

    def _present_single_in_view(
        self,
        to_show: MODEL_CLASS,
        should_focus: bool = False,
    ) -> None:
        self.p.add_new_item(
            to_show, should_focus=should_focus
        )
        self.all_records.append(to_show)

    def present_all(self):
        for record in self.MODEL_CLASS.from_db():
            self._present_single_in_view(record)

    def add_new_entry(self):
        add_dlg = self.view_collections.add(parent=self.p)
        add_dlg.set_values({"HasBreaks": 0})
        with add_dlg as dlg:
            dlg: self.view_collections.add
            if dlg.ShowModal() == dlg.AffirmativeId:
                new_entity = self.MODEL_CLASS(**dlg.get_values())
                new_entity.insert_into_db()
                self._present_single_in_view(new_entity, should_focus=True)

    def _on_click_handler_factory(self, method_name: str):
        return lambda e: getattr(self, method_name)()

    def on_edit(self):
        edit_dlg = self.view_collections.edit(parent=self.p)
        current_entity_state = self.focused_entity.cols_to_attrs()
        edit_dlg.set_values(current_entity_state)
        with edit_dlg as dlg:
            dlg: self.view_collections.edit
            if dlg.ShowModal() == dlg.AffirmativeId:
                new_values = dlg.get_values()
                self.focused_entity.update_db_record(new_values=new_values)
                self.p.update_shown_entity(
                    self.focused_entity,
                    self._focused_entity_index
                )

    def show_context_menu_for_entity(self, menu_pos: wx.Point) -> None:
        if self.any_focused:
            specs = []
            handlers = []
            for item_spec in self.view_collections.context_menu_spec:
                specs.append(item_spec)
                handlers.append(self._on_click_handler_factory(
                    item_spec.on_activate_listener_name
                ))
            menu = frontend.gui_control_factories.wx_context_menu_factory(
                item_specs=specs,
                on_click_listeners=handlers
            )
            self.p.PopupMenu(
                menu,
                menu_pos
            )

    def on_delete(self) -> None:
        index_to_remove = self._focused_entity_index
        print(f"Going to remove {index_to_remove}")
        self.all_records[index_to_remove].delete_db_record()
        del self.all_records[index_to_remove]
        self.p.delete_item(index_to_remove)
