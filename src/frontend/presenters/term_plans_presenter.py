from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import views.term_plan
import models.TermPlan
import presentation_manager
import gui_controls_spec


class TermPlanPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        models.TermPlan.TermPlan
    ] = models.TermPlan.TermPlan
    view_collections = views.term_plan
    all_records: List[models.TermPlan.TermPlan]

    def __init__(
        self,
        parent_presenter: presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.parent_presenter.focused_entity
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)

    def on_show_plan_entries(self):
        import presenters.term_plan_detail_presenter
        p = presenters.term_plan_detail_presenter.TermPlanDetailsPresenter(self)
        presentation_manager.get_presentation_manager().present(p)
