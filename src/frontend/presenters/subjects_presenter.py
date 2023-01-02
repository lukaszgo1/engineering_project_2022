from __future__ import annotations

from typing import (
    List,
)

import frontend.presenters.base_presenter
import frontend.views.subjects
import backend.models.subject


class SubjectsPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS = backend.models.subject.Subject
    view_collections = frontend.views.subjects
    all_records: List[MODEL_CLASS]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            SubjectName=entered_vals["SubjectName"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)
