import frontend.gui_controls_spec
import frontend.views._base_views


class AssignClassToTermPlanDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Powiąż z podstawą"
    affirmative_btn_label: str = "Powiąż"
    control_specs: tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledComboBoxSpec(
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