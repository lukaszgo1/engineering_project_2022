from __future__ import annotations

from typing import (
    List,
)

import models.institution
import views.institutions
import gui_control_factories
import presentation_manager
import presenters.base_presenter


class InstitutionPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: type[models.institution.Institution] = models.institution.Institution
    view_collections = views.institutions
    all_records: list[models.institution.Institution]

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    @property
    def initial_vals_for_add(self):
        return {"HasBreaks": 0}

    def on_show_long_breaks(self):
        import presenters.breaks_presenter
        p = presenters.breaks_presenter.BreaksPresenter()
        presentation_manager.get_presentation_manager().present(p)

    def on_show_classes(self):
        import presenters.classes_presenter
        p = presenters.classes_presenter.ClassesPresenter(self)
        presentation_manager.get_presentation_manager().present(p)

    def on_show_subjects(self):
        import presenters.subjects_presenter
        p = presenters.subjects_presenter.SubjectsPresenter(self)
        presentation_manager.get_presentation_manager().present(p)

    def on_show_teachers(self):
        import presenters.teachers_presenter
        p = presenters.teachers_presenter.TeachersPresenter(self)
        presentation_manager.get_presentation_manager().present(p)

    def on_show_class_rooms(self):
        import presenters.class_rooms_presenter
        p = presenters.class_rooms_presenter.ClassRoomsPresenter()
        presentation_manager.get_presentation_manager().present(p)

    def on_show_terms(self):
        import presenters.terms_presenter
        p = presenters.terms_presenter.TermsPresenter(self)
        presentation_manager.get_presentation_manager().present(p)
