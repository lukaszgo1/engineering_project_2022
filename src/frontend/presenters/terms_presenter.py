from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import views.terms
import backend.models.Term


class TermsPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.Term.Term
    ] = backend.models.Term.Term
    view_collections = views.terms
    all_records: List[backend.models.Term.Term]

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
        yield from self.MODEL_CLASS.from_endpoint(
            self.parent_presenter.focused_entity
        )

    def on_show_term_plans(self):
        import presentation_manager
        import presenters.term_plans_presenter
        p = presenters.term_plans_presenter.TermPlanPresenter(self)
        presentation_manager.get_presentation_manager().present(p)

    def on_add_new_schedule_entry(self):
        import presenters.schedule_presenter
        p = presenters.schedule_presenter.SchedulePresenter(self)
        p.add_new_entry()
