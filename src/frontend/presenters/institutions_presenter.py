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
