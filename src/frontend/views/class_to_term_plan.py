import gui_controls_spec
import views._base_views


class AssignClassToTermPlanDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Powiąż z podstawą"
    affirmative_btn_label: str = "Powiąż"
    control_specs: tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledComboBoxSpec(
            label="Podstawy:",
            identifier="TermPlanId"
        ),
    )


class RemoveAssignmentDlg(AssignClassToTermPlanDlg):

    title: str = "Usuń powiązanie z podstawą"
    affirmative_btn_label: str = "Usuń powiązanie"


add = AssignClassToTermPlanDlg
remove = RemoveAssignmentDlg


context_menu_spec = ()