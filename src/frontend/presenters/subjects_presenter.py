from __future__ import annotations

from typing import (
    List,
)

import presenters.base_presenter
import views.subjects
import models.subject


class SubjectsPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS = models.subject.Subject
    view_collections = views.subjects
    all_records: list[models.subject.Subject]

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
