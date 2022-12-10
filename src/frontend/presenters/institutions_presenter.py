from __future__ import annotations

from typing import (
    List,
)

import backend.models.institution
import frontend.views.institutions
import frontend.gui_control_factories
import frontend.presenters.base_presenter


class InstitutionPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS = backend.models.institution.Institution
    view_collections = frontend.views.institutions
    all_records: List[MODEL_CLASS]

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(**entered_vals)

    @property
    def initial_vals_for_add(self):
        return {"HasBreaks": 0}

    def on_add_break(self):
        import frontend.presenters.breaks_presenter
        p = frontend.presenters.breaks_presenter.BreaksPresenter(self)
        p.add_new_entry()

    def on_show_long_breaks(self):
        import frontend.presentation_manager
        import frontend.presenters.breaks_presenter
        p = frontend.presenters.breaks_presenter.BreaksPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_new_class(self):
        import frontend.presenters.classes_presenter
        p = frontend.presenters.classes_presenter.ClassesPresenter(self)
        p.add_new_entry()

    def on_show_classes(self):
        import frontend.presentation_manager
        import frontend.presenters.classes_presenter
        p = frontend.presenters.classes_presenter.ClassesPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_new_subject(self):
        import frontend.presenters.subjects_presenter
        p = frontend.presenters.subjects_presenter.SubjectsPresenter(self)
        p.add_new_entry()

    def on_show_subjects(self):
        import frontend.presentation_manager
        import frontend.presenters.subjects_presenter
        p = frontend.presenters.subjects_presenter.SubjectsPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_new_teacher(self):
        import frontend.presenters.teachers_presenter
        p = frontend.presenters.teachers_presenter.TeachersPresenter(self)
        p.add_new_entry()

    def on_show_teachers(self):
        import frontend.presentation_manager
        import frontend.presenters.teachers_presenter
        p = frontend.presenters.teachers_presenter.TeachersPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_add_class_room(self):
        import frontend.presenters.class_rooms_presenter
        p = frontend.presenters.class_rooms_presenter.ClassRoomsPresenter(self)
        p.add_new_entry()

    def on_show_class_rooms(self):
        import frontend.presentation_manager
        import frontend.presenters.class_rooms_presenter
        p = frontend.presenters.class_rooms_presenter.ClassRoomsPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)

    def on_add_new_term(self):
        import frontend.presenters.terms_presenter
        p = frontend.presenters.terms_presenter.TermsPresenter(self)
        p.add_new_entry()

    def on_show_terms(self):
        import frontend.presentation_manager
        import frontend.presenters.terms_presenter
        p = frontend.presenters.terms_presenter.TermsPresenter(self)
        frontend.presentation_manager.get_presentation_manager().present(p)
