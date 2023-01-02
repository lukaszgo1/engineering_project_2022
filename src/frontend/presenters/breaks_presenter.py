from __future__ import annotations

import datetime
import operator
from typing import (
    ClassVar,
    List,
    Type,
)

import attrs

import frontend.presenters.base_presenter
import frontend.presenters.institutions_presenter
import frontend.views.breaks
import frontend.gui_controls_spec
import frontend.presentation_manager
import backend.models.break_model
import backend.models.institution


@attrs.define(kw_only=True, str=False)
class BreakRepresentation:

    start: datetime.datetime
    end: datetime.datetime
    date_format: ClassVar[str] = "%H:%M"

    @property
    def start_as_string(self) -> str:
        return self.start.strftime(self.date_format)

    @property
    def end_as_string(self) -> str:
        return self.end.strftime(self.date_format)

    def __str__(self) -> str:
        return f"{self.start_as_string} - {self.end_as_string}"


class BreaksPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.break_model.Break
    ] = backend.models.break_model.Break
    view_collections = frontend.views.breaks
    all_records: List[backend.models.break_model.Break]

    @property
    def initial_vals_for_add(self):
        possible_lengths = self.possible_break_lengths()
        possible_lengths = frontend.gui_controls_spec.ComboBoxvaluesSpec(possible_lengths)
        return {"break_length": possible_lengths}

    @property
    def break_for_inst(self) -> backend.models.institution.Institution:
        return frontend.presentation_manager.get_presentation_manager()._active_presenters[-2].focused_entity

    def possible_break_lengths(self) -> List[int]:
        normal_break = self.break_for_inst.NormalBreakLength
        lesson_len = self.break_for_inst.NormalLessonLength
        if normal_break is not None and lesson_len is not None:
            return [_ for _ in range(normal_break + 5, lesson_len, 5)]
        raise RuntimeError("Attempted to create break lengths for inst without breaks")

    def possible_breaks(self, length: int):
        normal_break = self.break_for_inst.NormalBreakLength
        lesson_len = self.break_for_inst.NormalLessonLength
        existing_breaks = list(
            self.MODEL_CLASS.from_db(self.break_for_inst)
        )
        if existing_breaks:
            existing_breaks.sort(key=operator.attrgetter("BreakStartingHour"))
            starting_hour = existing_breaks[-1].BreakEndingHour
        else:
            starting_hour = self.break_for_inst.StartingHour
        ending_hour = self.break_for_inst.EndingHour
        default_date = "2000-01-02 "
        start_obj = datetime.datetime.fromisoformat(
            f"{default_date}{starting_hour}"
        )
        end_obj = datetime.datetime.fromisoformat(
            f"{default_date}{ending_hour}"
        )
        long_break_td = datetime.timedelta(minutes=length)
        normal_break_td = datetime.timedelta(minutes=normal_break)
        lesson_td = datetime.timedelta(minutes=lesson_len)
        res = []
        lesson_start = (start_obj + normal_break_td + lesson_td)
        while lesson_start < end_obj:
            lesson_start = lesson_start + lesson_td
            possible_break_start = lesson_start
            possible_end = (lesson_start + long_break_td)
            if possible_end >= end_obj:
                break
            lesson_start = lesson_start + normal_break_td
            if lesson_start >= end_obj:
                break
            res.append(
                BreakRepresentation(
                    start=possible_break_start, end=possible_end
                )
            )
        return res[:-1]

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            BreakStartingHour=entered_vals["BreakStartingHour"],
            BreakEndingHour=entered_vals["BreakEndingHour"],
            owner=self.break_for_inst
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.break_for_inst)
