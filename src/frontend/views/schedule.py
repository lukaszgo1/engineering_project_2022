import operator
from typing import (
    Dict,
    List,
    Tuple,
)

import wx

import frontend.gui_controls_spec
import frontend.views._base_views


class SubjectsInClassFilterer(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_class_selected)

    def on_new_class_selected(self, class_model):
        for control in self._controls_to_modify:
            if control.identifier == "SubjectId":
                subjects = self._presenter.subjects_in_plan_for_class(class_model)
                control.set_value(
                    frontend.gui_controls_spec.ComboBoxvaluesSpec(subjects)
                )
                break


class TeachersAssignedToSubject(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_subject_selected)

    def on_new_subject_selected(self, subject):
        for control in self._controls_to_modify:
            if control.identifier == "TeacherId":
                teachers = self._presenter.teachers_allowed_to_teach(subject)
                control.set_value(
                    frontend.gui_controls_spec.ComboBoxvaluesSpec(teachers)
                )
            if control.identifier == "ClassRoomId":
                class_rooms = self._presenter.class_rooms_for_subject(subject)
                control.set_value(
                    frontend.gui_controls_spec.ComboBoxvaluesSpec(class_rooms)
                )


class EndLessonTimeFilterer(frontend.gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_lesson_beginning_selected)

    def on_new_lesson_beginning_selected(self, lesson_start):
        to_modify = None
        for control in self._controls_to_modify:
            if control.identifier == "LessonEndingHour":
                to_modify = control
            if control.identifier == "SubjectId":
                subject = control.get_value()
            if control.identifier == "ClassId":
                selected_class = control.get_value()
        if to_modify is None:
            raise RuntimeError("Failed to find combo box with end times")
        to_modify.set_value(
            frontend.gui_controls_spec.ComboBoxvaluesSpec(
                self._presenter.get_possible_ends_for_lesson(
                    selected_class,
                    subject,
                    lesson_start
                )
            )
        )


class AddScheduleEntryDlg(frontend.views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj zajęcia do grafiku"
    affirmative_btn_label: str = "Dodaj"
    control_specs: tuple[
        frontend.gui_controls_spec._ControlWrapperBase, ...
    ] = (
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Grupa:",
            identifier="ClassId",
            on_change_notifier=SubjectsInClassFilterer,
            should_react_to_changes=True
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Przedmiot:",
            identifier="SubjectId",
            should_react_to_changes=True,
            on_change_notifier=TeachersAssignedToSubject
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Prowadzący:",
            identifier="TeacherId",
            should_react_to_changes=True
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Sala:",
            identifier="ClassRoomId",
            should_react_to_changes=True
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Dzień tygodnia:",
            identifier="WeekDay"
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            label="Godzina rozpoczęcia:",
            identifier="LessonStartingHour",
            on_change_notifier=EndLessonTimeFilterer
        ),
        frontend.gui_controls_spec.LabeledComboBoxSpec(
            identifier="LessonEndingHour",
            label="Godzina zakończenia:",
            should_react_to_changes=True
        ),
    )

    def get_values(self) -> Dict:
        res = super().get_values()
        res["MainSubjectId"] = res["PrimaryCourse"].id
        return res


class ClassRoomsListing(frontend.views._base_views.BaseEntityList):

    buttons_in_view: List[frontend.gui_controls_spec.WXButtonSpec] = [
        frontend.gui_controls_spec.WXButtonSpec(
            label="Dodaj salę",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        )
    ]

    list_view_columns: List[frontend.gui_controls_spec.WXListColumnSpec] = [
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Numer",
            width=400,
            value_getter=operator.attrgetter("ClassRoomIdentifier")
        ),
        frontend.gui_controls_spec.WXListColumnSpec(
            header_name="Główny kurs",
            width=400,
            value_getter=operator.attrgetter("PrimaryCourse"),
            value_converter=str
        )
    ]


items_list: Tuple[frontend.gui_controls_spec.MenuItemSpec, ...] = (
    frontend.gui_controls_spec.MenuItemSpec(
        id=wx.ID_EDIT,
        name="Edytuj",
        on_activate_listener_name="on_edit"
    ),
    frontend.gui_controls_spec.MenuItemSpec(
        id=wx.ID_DELETE,
        name="Usuń",
        on_activate_listener_name="on_delete"
    ),
)


class EditClassDlg(AddScheduleEntryDlg):

    title: str = "Edytuj salę lekcyjną"
    affirmative_btn_label: str = "Zapisz zmiany"


add = AddScheduleEntryDlg
listing = ClassRoomsListing
context_menu_spec = items_list
edit = EditClassDlg
