from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.term_plan_details
import frontend.gui_controls_spec
import backend.models.term_plan_detail


class TermPlanDetailsPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.term_plan_detail.TermPlanDetail
    ] = backend.models.term_plan_detail.TermPlanDetail
    view_collections = frontend.views.term_plan_details
    all_records: List[backend.models.term_plan_detail.TermPlanDetail]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            LessonsAmount=entered_vals["LessonsAmount"],
            LessonsWeekly=entered_vals["LessonsWeekly"],
            MaxBlockSize=entered_vals["MaxBlockSize"],
            MinBlockSize=entered_vals["MinBlockSize"],
            PreferredDistanceInDays=entered_vals["PreferredDistanceInDays"],
            PreferredDistanceInWeeks=entered_vals["PreferredDistanceInWeeks"],
            SubjectId=entered_vals["SubjectId"],
            EntryDescribingSubjectId=entered_vals["SubjectId"].id,
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )

    @property
    def initial_vals_for_add(self):
        subjs_in_inst = frontend.gui_controls_spec.ComboBoxvaluesSpec(
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
