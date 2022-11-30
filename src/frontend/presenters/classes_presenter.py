from __future__ import annotations

from typing import (
    List,
)

import frontend.presenters.base_presenter
import frontend.views.classes
import backend.models.class_model


class ClassesPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS = backend.models.class_model.Class
    view_collections = frontend.views.classes
    all_records: List[MODEL_CLASS]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            ClassIdentifier=entered_vals["ClassIdentifier"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )
