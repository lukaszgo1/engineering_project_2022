from __future__ import annotations

import datetime
import email.utils
from typing import (
    ClassVar,
    List,
    Type,
)

import attrs

import presenters.base_presenter
import presenters.institutions_presenter
import views.breaks
import gui_controls_spec
import presentation_manager
import backend.models.break_model
import backend.models.institution
import api_utils


@attrs.define(kw_only=True, str=False)
class BreakRepresentation:

    start: datetime.time
    end: datetime.time
    date_format: ClassVar[str] = "%H:%M"

    @property
    def start_as_string(self) -> str:
        return self.start.strftime(self.date_format)

    @property
    def end_as_string(self) -> str:
        return self.end.strftime(self.date_format)

    def __str__(self) -> str:
        return f"{self.start_as_string} - {self.end_as_string}"

    @classmethod
    def from_http_date(cls, start, end):
        start_tpl = email.utils.parsedate(start)
        end_tpl = email.utils.parsedate(end)
        return cls(
            start=datetime.time(start_tpl[3], start_tpl[4]),
            end=datetime.time(end_tpl[3], end_tpl[4]),
        )


class BreaksPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.break_model.Break
    ] = backend.models.break_model.Break
    view_collections = views.breaks
    all_records: List[backend.models.break_model.Break]

    @property
    def initial_vals_for_add(self):
        possible_lengths = self.possible_break_lengths()
        possible_lengths = gui_controls_spec.ComboBoxvaluesSpec(possible_lengths)
        return {"break_length": possible_lengths}

    @property
    def break_for_inst(self) -> backend.models.institution.Institution:
        return presentation_manager.get_presentation_manager()._active_presenters[-2].focused_entity

    def possible_break_lengths(self) -> List[int]:
        normal_break = self.break_for_inst.NormalBreakLength
        lesson_len = self.break_for_inst.NormalLessonLength
        if normal_break is not None and lesson_len is not None:
            return [_ for _ in range(normal_break + 5, lesson_len, 5)]
        raise RuntimeError("Attempted to create break lengths for inst without breaks")

    def possible_breaks(self, length: int):
        for start, end in api_utils.get_data(
            end_point_name="get_possible_breaks",
            params={"inst_id": self.break_for_inst.id, "break_length": length}
        )["Breaks"]:
            yield BreakRepresentation.from_http_date(
                start=start, end=end
            )

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.break_for_inst
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.break_for_inst)
