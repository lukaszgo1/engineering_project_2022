from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import views.term_plan_details
import gui_controls_spec
import models.term_plan_detail


class TermPlanDetailsPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        models.term_plan_detail.TermPlanDetail
    ] = models.term_plan_detail.TermPlanDetail
    view_collections = views.term_plan_details
    all_records: List[models.term_plan_detail.TermPlanDetail]

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

    @property
    def initial_vals_for_add(self):
        subjs_in_inst = gui_controls_spec.ComboBoxvaluesSpec(
            list(self.parent_presenter.parent_presenter.focused_entity.owner.subjects_taught_in_inst())
        )
        return {
            "SubjectId": subjs_in_inst,
            "DistanceIn": self.view_collections.PossibleDistance.DAYS
        }

    def vals_for_edit(self):
        res = super().vals_for_edit()
        possible_course_choices = self.initial_vals_for_add["SubjectId"]
        chosen_course_id = res["SubjectId"].id
        for index, course in enumerate(possible_course_choices.values):
            if course.id == chosen_course_id:
                possible_course_choices.initial_selection = index
                break
        res["SubjectId"] = possible_course_choices
        if res["PreferredDistanceInDays"] is None:
            res["DistanceIn"] = self.view_collections.PossibleDistance.WEEKS
            del res["PreferredDistanceInDays"]
        elif res["PreferredDistanceInWeeks"] is None:
            res["DistanceIn"] = self.view_collections.PossibleDistance.DAYS
            del res["PreferredDistanceInWeeks"]
        return res
