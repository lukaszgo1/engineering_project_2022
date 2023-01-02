from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.teachers
import backend.models.teacher


class TeachersPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.teacher.Teacher
    ] = backend.models.teacher.Teacher
    view_collections = frontend.views.teachers
    all_records: List[backend.models.teacher.Teacher]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            FirstName=entered_vals["FirstName"],
            LastName=entered_vals["LastName"],
            IsAvailable=entered_vals["IsAvailable"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)

    @property
    def initial_vals_for_add(self):
        return {"IsAvailable": True}

    def on_assign_to_subject(self):
        import frontend.presenters.teacher_to_subject_presenter
        p = frontend.presenters.teacher_to_subject_presenter.TeacherToSubjectsPresenter(self)
        p.add_new_entry()

    def on_remove_subject_assignment(self):
        import frontend.presenters.teacher_to_subject_presenter
        p = frontend.presenters.teacher_to_subject_presenter.TeacherToSubjectsPresenter(self)
        p.remove_entry()
