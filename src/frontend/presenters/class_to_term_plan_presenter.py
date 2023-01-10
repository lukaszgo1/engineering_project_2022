from __future__ import annotations

import presenters.base_presenter
import presentation_manager
import views.class_to_term_plan
import gui_controls_spec
import backend.models.class_to_term_plan


class ClassToTermPlanPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: type[
        backend.models.class_to_term_plan.ClassToTermPlan
    ] = backend.models.class_to_term_plan.ClassToTermPlan
    view_collections = views.class_to_term_plan
    all_records: list[backend.models.class_to_term_plan.ClassToTermPlan]

    def __init__(
        self,
        parent_presenter: presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def add_new_entry(self):
        super().add_new_entry()
        presentation_manager.get_presentation_manager()._active_presenters[-1].set_toolbar_icons_state()

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            TermPlanId=entered_vals["TermPlanId"],
            AssociatedTermPlanId=entered_vals["TermPlanId"].id,
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        raise RuntimeError(
            "This code should not be reached"
        )
#        yield from self.MODEL_CLASS.from_endpoint(
#            self.parent_presenter.focused_entity
        #)

    @property
    def initial_vals_for_add(self):
        term_plans_in_inst = list(
            self.parent_presenter.focused_entity.owner.term_plans_in_inst()
        )
        combobox_vals = gui_controls_spec.ComboBoxvaluesSpec(
            values=term_plans_in_inst,
        )
        return {"TermPlanId": combobox_vals}

    def remove_entry(self):
        associated_term_plan = self.parent_presenter.focused_entity.assigned_term_plan
        associated_term_plan.delete_db_record()
        self.set_toolbar_icons_state()
