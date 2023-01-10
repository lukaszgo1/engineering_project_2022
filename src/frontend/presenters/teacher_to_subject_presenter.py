from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import views.teacher_to_subjects
import gui_controls_spec
import backend.models.teacher_to_subject
import backend.models.subject


class TeacherToSubjectsPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.teacher_to_subject.TeacherToSubject
    ] = backend.models.teacher_to_subject.TeacherToSubject
    view_collections = views.teacher_to_subjects
    all_records: List[backend.models.teacher_to_subject.TeacherToSubject]

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

    @property
    def initial_vals_for_add(self):
        not_assigned_subjs = list(
            backend.models.subject.Subject.get_not_assigned_to_teacher(
                self.parent_presenter.focused_entity
            )
        )
        combobox_vals = gui_controls_spec.ComboBoxvaluesSpec(
            values=not_assigned_subjs,
        )
        return {"SubjectId": combobox_vals}

    def remove_entry(self):
        assigned_to_teacher = list(self.MODEL_CLASS.from_endpoint(
            self.parent_presenter.focused_entity
        ))
        combobox_vals = gui_controls_spec.ComboBoxvaluesSpec(
            values=assigned_to_teacher,
        )
        remove_dlg = self.view_collections.remove(
            parent=self.new_windows_parent,
            presenter=self
        )
        remove_dlg.set_values(
            {"SubjectId": combobox_vals}
        )
        with remove_dlg as dlg:
            if dlg.ShowModal() == dlg.AffirmativeId:
                dlg.get_values()["SubjectId"].delete_db_record()
