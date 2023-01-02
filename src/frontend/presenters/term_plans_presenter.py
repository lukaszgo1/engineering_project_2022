from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.term_plan
import backend.models.TermPlan


class TermPlanPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.TermPlan.TermPlan
    ] = backend.models.TermPlan.TermPlan
    view_collections = frontend.views.term_plan
    all_records: List[backend.models.TermPlan.TermPlan]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            TermPlanName=entered_vals["TermPlanName"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)

    def on_add_new_plan_entry(self):
        import frontend.presenters.term_plan_detail_presenter
        p = frontend.presenters.term_plan_detail_presenter.TermPlanDetailsPresenter(self)
        p.add_new_entry()

    def on_show_plan_entries(self):
        import frontend.presentation_manager
        import frontend.presenters.term_plan_detail_presenter
        p = frontend.presenters.term_plan_detail_presenter.TermPlanDetailsPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)
