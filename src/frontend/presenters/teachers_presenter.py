from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import views.teachers
import backend.models.teacher
import gui_controls_spec
import presenters.schedule_presenter


class TeachersPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.teacher.Teacher
    ] = backend.models.teacher.Teacher
    view_collections = views.teachers
    all_records: List[backend.models.teacher.Teacher]
    detail_presenters = (presenters.schedule_presenter.SchedForTeacherPres,)

    def __init__(
        self,
        parent_presenter: presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.parent_presenter.focused_entity
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    def on_new_term_selected(self, term_obj):
        if term_obj is None:
            return
        self.det.for_term = term_obj
        self.det.term_in_inst = self.det.for_term.owner
        self.det.populate_on_change()

    def master_item_changed(self, index):
        self.det.teacher =  self.all_records[index]
        self.det.populate_on_change()

    def handle_detail_presenter(self, detail_pres):
        self.det = detail_pres
        try:
            self.det.teacher =  self.focused_entity
        except RuntimeError:
            pass
        c = None
        for c in detail_pres.conts:
            if c.identifier == "terms":
                break
        if c is None:
            raise RuntimeError
        c.register_to_changes(self.on_new_term_selected)
        c.set_value(
            gui_controls_spec.ComboBoxvaluesSpec(
                list(self.parent_presenter.focused_entity.terms_in_inst()),
                initial_selection=0
            )
        )
        self.p.on_item_focused_listeners.append(self.master_item_changed)

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.parent_presenter.focused_entity)

    @property
    def initial_vals_for_add(self):
        return {"IsAvailable": True}

    def on_assign_to_subject(self):
        import presenters.teacher_to_subject_presenter
        p = presenters.teacher_to_subject_presenter.TeacherToSubjectsPresenter(self)
        p.add_new_entry()

    def on_remove_subject_assignment(self):
        import presenters.teacher_to_subject_presenter
        p = presenters.teacher_to_subject_presenter.TeacherToSubjectsPresenter(self)
        p.remove_entry()
