from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.teacher_to_subjects
import frontend.gui_controls_spec
import backend.models.teacher_to_subject
import backend.models.subject


class TeacherToSubjectsPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.teacher_to_subject.TeacherToSubject
    ] = backend.models.teacher_to_subject.TeacherToSubject
    view_collections = frontend.views.teacher_to_subjects
    all_records: List[backend.models.teacher_to_subject.TeacherToSubject]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            SubjectId=entered_vals["SubjectId"],
            AssignedSubjectId=entered_vals["SubjectId"].id,
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )

    @property
    def initial_vals_for_add(self):
        assigned_to_teacher = list(self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        ))
        assigned_ids = {_.AssignedSubjectId for _ in assigned_to_teacher}
        courses_list = list(
            backend.models.subject.Subject.from_db(
                self.parent_presenter.focused_entity.owner
            )
        )
        courses_list = [_ for _ in courses_list if _.id not in assigned_ids]
        combobox_vals = frontend.gui_controls_spec.ComboBoxvaluesSpec(
            values=courses_list,
        )
        return {"SubjectId": combobox_vals}

    def remove_entry(self):
        assigned_to_teacher = list(self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        ))
        combobox_vals = frontend.gui_controls_spec.ComboBoxvaluesSpec(
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
