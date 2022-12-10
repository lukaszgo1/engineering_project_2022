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
