from typing import (
    Tuple,
)

import frontend.gui_controls_spec
import frontend.views._base_views


class AssignTeacherToSubjectDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Przypisz do kursu"
    affirmative_btn_label: str = "Przypisz"
    control_specs: Tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Kurs:",
            identifier="SubjectId"
        ),
    )


class RemoveAssignmentDlg(AssignTeacherToSubjectDlg):

    title: str = "Usuń przypisanie do przedmiotu"
    affirmative_btn_label: str = "Usuń przypisanie"


add = AssignTeacherToSubjectDlg
remove = RemoveAssignmentDlg
context_menu_spec = ()
