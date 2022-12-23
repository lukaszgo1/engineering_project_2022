from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.terms
import backend.models.Term


class TermsPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.Term.Term
    ] = backend.models.Term.Term
    view_collections = frontend.views.terms
    all_records: List[backend.models.Term.Term]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            StartDate=entered_vals["StartDate"],
            EndDate=entered_vals["EndDate"],
            TermName=entered_vals["TermName"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )

    def on_add_new_term_plan(self):
        import frontend.presenters.term_plans_presenter
        p = frontend.presenters.term_plans_presenter.TermPlanPresenter(self)
        p.add_new_entry()

    def on_show_term_plans(self):
        import frontend.presentation_manager
        import frontend.presenters.term_plans_presenter
        p = frontend.presenters.term_plans_presenter.TermPlanPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_add_new_schedule_entry(self):
        import frontend.presenters.schedule_presenter
        p = frontend.presenters.schedule_presenter.SchedulePresenter(self)
        p.add_new_entry()
