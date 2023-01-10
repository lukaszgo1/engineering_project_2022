from typing import (
    Tuple,
)

import gui_controls_spec
import views._base_views


class AssignTeacherToSubjectDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Przypisz do kursu"
    affirmative_btn_label: str = "Przypisz"
    control_specs: Tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledComboBoxSpec(
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
