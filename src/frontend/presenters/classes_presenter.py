from __future__ import annotations

from typing import (
    List,
)

import presenters.base_presenter
import views.classes
import models.class_model
import presenters.schedule_presenter
import gui_controls_spec


class ClassesPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS = models.class_model.Class
    view_collections = views.classes
    all_records: List[MODEL_CLASS]
    detail_presenters = (presenters.schedule_presenter.SchedForClassPres,)

    def __init__(
        self,
        parent_presenter: presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def on_new_term_selected(self, term_obj):
        if term_obj  is None:
            return
        self.det.for_term = term_obj
        self.det.term_in_inst = self.det.for_term.owner
        self.det.populate_on_change()

    def master_item_changed(self, index):
        self.det.class_mod =  self.all_records[index]
        self.det.populate_on_change()

    def handle_detail_presenter(self, detail_pres):
        self.det = detail_pres
        try:
            self.det.class_mod =  self.focused_entity
        except RuntimeError:
            pass
        c = None
        for c in detail_pres.conts:
            if c.identifier == "terms":
                break
        if c is None:
            raise RuntimeError
        c.register_to_changes(self.on_new_term_selected)
        c.set_value(
            gui_controls_spec.ComboBoxvaluesSpec(
                list(self.parent_presenter.focused_entity.terms_in_inst()),
                initial_selection=0
            )
        )
        self.p.on_item_focused_listeners.append(self.master_item_changed)

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.parent_presenter.focused_entity
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)

    def associate_with_term_plan(self):
        import presenters.class_to_term_plan_presenter
        p = presenters.class_to_term_plan_presenter.ClassToTermPlanPresenter(self)
        p.add_new_entry()

    def remove_association_with_term_plan(self):
        import presenters.class_to_term_plan_presenter
        p = presenters.class_to_term_plan_presenter.ClassToTermPlanPresenter(self)
        p.remove_entry()
