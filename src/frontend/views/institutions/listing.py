import operator

from typing import (
    List,
)

import frontend.views._base_views as base_views
import frontend.gui_controls_spec as ctrl_specs


def _to_string_if_truthy(val) -> str:
    if val:
        return str(val)
    return ""


class InstitutionsListing(base_views.BaseEntityList):

    buttons_in_view: List[ctrl_specs.WXButtonSpec] = [
        ctrl_specs.WXButtonSpec(
            label='Dodaj nową instytucję',
            on_press=lambda evt: print(evt)
        )
    ]

    list_view_columns: List[ctrl_specs.WXListColumnSpec] = [
        ctrl_specs.WXListColumnSpec(
            header_name='Nazwa',
            width=400,
            value_getter=operator.attrgetter("InstitutionName")
        ),
        ctrl_specs.WXListColumnSpec(
            header_name='Godzina rozpoczęcia zajęć',
            width=200,
            value_getter=operator.attrgetter("StartingHour")
        ),
        ctrl_specs.WXListColumnSpec(
            header_name='Godzina zakończenia zajęć',
            width=200,
            value_getter=operator.attrgetter("EndingHour")
        ),
        ctrl_specs.WXListColumnSpec(
            header_name='Czy przerwy',
            width=150,
            value_getter=operator.attrgetter("HasBreaks"),
            value_converter=lambda val: "Tak" if val else "Nie"
        ),
        ctrl_specs.WXListColumnSpec(
            header_name='Długość przerwy',
            width=150,
            value_getter=operator.attrgetter("NormalBreakLength"),
            value_converter=_to_string_if_truthy
        ),
        ctrl_specs.WXListColumnSpec(
            header_name='Długość zajęć',
            width=150,
            value_getter=operator.attrgetter("NormalLessonLength"),
            value_converter=_to_string_if_truthy
        ),
    ]
