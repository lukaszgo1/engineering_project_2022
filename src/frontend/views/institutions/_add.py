from typing import (
    Tuple,
)

import frontend.gui_controls_spec
import frontend.views._base_views


class AddInst(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj instytucję"
    affirmative_btn_label: str = "Dodaj"

    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="InstitutionName",
            label="Nazwa instytucji:"
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="StartingHour",
            label="Godzina rozpoczęcia zajęć:"
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="EndingHour",
            label="Godzina końca zajęć:"
        ),
        frontend.gui_controls_spec.CheckBoxSpec(
            identifier="HasBreaks",
            label="Czy przerwy",
            has_dependent_controls=True
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="NormalBreakLength",
            label="Długość przerwy:",
            listeners_to_register=["set_state"]
        ),
        frontend.gui_controls_spec.LabeledEditFieldSpec(
            identifier="NormalLessonLength",
            label="Długość zajęć:",
            listeners_to_register=["set_state"]
        ),
    )
