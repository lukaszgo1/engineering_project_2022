import operator
from typing import (
    Dict,
    List,
    Tuple,
)

import attrs
import wx

import gui_controls_spec
import views._base_views
import presentation_manager


@attrs.define(kw_only=True)
class ScheduleExporter:

    label: str
    default_file_name: str
    wildcard: str
    export_end_point: str

    def do_export(self, parent: wx.Window, content_to_write: str) -> None:
        with wx.FileDialog(
            parent,
            "Wybierz plik, do którego chcesz zapisać grafik",
            defaultFile=self.default_file_name,
            wildcard=self.wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return None
            pathname = fileDialog.GetPath()
            with open(pathname, "w", newline='', encoding='utf-8') as file:
                file.write(content_to_write)


exporters = (
    ScheduleExporter(
        label="CSV",
        wildcard="plik csv (*.csv)|*.csv",
        default_file_name="*.csv",
        export_end_point="export_to_csv"
    ),
    ScheduleExporter(
        export_end_point="export_to_calendar",
        label="Plik kalendarza",
        default_file_name="*.ics",
        wildcard="plik ics (*.ics)|*.ics"
    ),
)


class LessonsBeginningSetterMixIn:
    """This class is responsible for setting possible lesson starts
    in the schedule entry dialog.
    This is just a mix-in and therefore
    has to be added to MRO of a specific change listener to be usefull.
    """

    # Universal signature to support being added
    # to a notifier for an arbitrary control
    def populate_lesson_combo_box(self, *args, **kwargs):
        selected_class = self.registered_control_by_identifier("ClassId").value
        selected_subject = self.registered_control_by_identifier("SubjectId").value
        selected_teacher = self.registered_control_by_identifier("TeacherId").value
        selected_class_room = self.registered_control_by_identifier("ClassRoomId").value
        selected_week_day =  self.registered_control_by_identifier("WeekDay").value
        # Explicitly check for `None` rather than just for falsy values,
        # since some enum members are falsy in a boolean context.
        if not all((
            _ is not None for _ in (
                selected_class,
                selected_class_room,
                selected_subject,
                selected_teacher,
                selected_week_day
            )
        )):
            return
        possible_starts = self._presenter.get_possible_lesson_beginnings(
            selected_class,
            selected_subject,
            selected_week_day,
            selected_teacher,
            selected_class_room
        )
        self.registered_control_by_identifier("LessonStartingHour").set_value(
            possible_starts
        )


class SubjectsInClassFilterer(
    gui_controls_spec.OnChangeListener,
    LessonsBeginningSetterMixIn
):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_class_selected)

    def on_new_class_selected(self, class_model):
        subjects = self._presenter.subjects_in_plan_for_class(class_model)
        self.registered_control_by_identifier("SubjectId").set_value(
            gui_controls_spec.ComboBoxvaluesSpec(subjects, initial_selection=0)
        )
        self.populate_lesson_combo_box()


class TeachersAssignedToSubject(
    gui_controls_spec.OnChangeListener,
    LessonsBeginningSetterMixIn
):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_subject_selected)

    def on_new_subject_selected(self, subject):
        teachers = self._presenter.teachers_allowed_to_teach(subject)
        self.registered_control_by_identifier("TeacherId").set_value(
            gui_controls_spec.ComboBoxvaluesSpec(teachers, initial_selection=0)
        )
        class_rooms = self._presenter.class_rooms_for_subject(subject)
        self.registered_control_by_identifier("ClassRoomId").set_value(
            gui_controls_spec.ComboBoxvaluesSpec(class_rooms, initial_selection=0)
        )
        selected_class = self.registered_control_by_identifier(
            "ClassId"
        ).value
        self.registered_control_by_identifier("WeekDay").set_value(
            self._presenter.get_possible_week_days_for_lesson(
                selected_class,
                subject
            )
        )
        self.populate_lesson_combo_box()


class EndLessonTimeFilterer(gui_controls_spec.OnChangeListener):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.on_new_lesson_beginning_selected)

    def on_new_lesson_beginning_selected(self, lesson_start):
        subject = self.registered_control_by_identifier("SubjectId").value
        selected_class = self.registered_control_by_identifier("ClassId").value
        self.registered_control_by_identifier("LessonEndingHour").set_value(
            gui_controls_spec.ComboBoxvaluesSpec(
                self._presenter.get_possible_ends_for_lesson(
                    selected_class,
                    subject,
                    lesson_start
                ),
                initial_selection=0
            )
        )


class LessonBeginningSetterWhenChanged(
    gui_controls_spec.OnChangeListener,
    LessonsBeginningSetterMixIn
    ):

    def __init__(self, presenter, emitting_control) -> None:
        super().__init__(presenter, emitting_control)
        self._emitting_control.register_to_changes(self.populate_lesson_combo_box)


class AddScheduleEntryDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Dodaj zajęcia do grafiku"
    affirmative_btn_label: str = "Dodaj"
    control_specs: tuple[
        gui_controls_spec._ControlWrapperBase, ...
    ] = (
        gui_controls_spec.LabeledComboBoxSpec(
            label="Grupa:",
            identifier="ClassId",
            on_change_notifier=SubjectsInClassFilterer,
            should_react_to_changes=True
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Przedmiot:",
            identifier="SubjectId",
            should_react_to_changes=True,
            on_change_notifier=TeachersAssignedToSubject
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Prowadzący:",
            identifier="TeacherId",
            should_react_to_changes=True,
            on_change_notifier=LessonBeginningSetterWhenChanged
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Sala:",
            identifier="ClassRoomId",
            should_react_to_changes=True,
            on_change_notifier=LessonBeginningSetterWhenChanged
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Dzień tygodnia:",
            identifier="WeekDay",
            should_react_to_changes=True,
            on_change_notifier=LessonBeginningSetterWhenChanged
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            label="Godzina rozpoczęcia:",
            identifier="LessonStartingHour",
            on_change_notifier=EndLessonTimeFilterer,
            should_react_to_changes=True
        ),
        gui_controls_spec.LabeledComboBoxSpec(
            identifier="LessonEndingHour",
            label="Godzina zakończenia:",
            should_react_to_changes=True
        ),
    )


class SchedulesListing(views._base_views.BaseEntityList):

    def get_parent(self):
        return presentation_manager.get_presentation_manager()._active_presenters[-1].p

    buttons_in_view: list[gui_controls_spec.WXButtonSpec] = [
        gui_controls_spec.WXButtonSpec(
            label="Dodaj zajęcia do grafiku",
            on_press=lambda e: e.EventObject.Parent.presenter.add_new_entry()
        ),
        gui_controls_spec.WXButtonSpec(
            label="Eksportuj grafik",
            on_press=lambda e: e.EventObject.Parent.presenter.on_export()
        ),
    ]

    list_view_columns: list[gui_controls_spec.WXListColumnSpec] = [
        gui_controls_spec.WXListColumnSpec(
            header_name="Dzień tygodnia",
            width=100,
            value_getter=operator.attrgetter("WeekDay"),
            value_converter=str
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Początek zajęć",
            width=100,
            value_getter=operator.attrgetter("LessonStartingHour"),
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Koniec zajęć",
            width=100,
            value_getter=operator.attrgetter("LessonEndingHour")
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Przedmiot",
            width=200,
            value_getter=operator.attrgetter("SubjectId"),
            value_converter=str
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Grupa",
            width=200,
            value_getter=operator.attrgetter("ClassId"),
            value_converter=str
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Prowadzący",
            width=200,
            value_getter=operator.attrgetter("TeacherId"),
            value_converter=str
        ),
        gui_controls_spec.WXListColumnSpec(
            header_name="Sala",
            width=200,
            value_getter=operator.attrgetter("ClassRoomId"),
            value_converter=str
        ),
    ]

    def show(self, view_pos):
        presentation_manager.get_presentation_manager()._active_presenters[-1].p.main_sizer.Add(self, 1, wx.EXPAND)
        self.populate_toolbar(self.presenter.toolbar_items_in_view)
        self.Show()


items_list: tuple[gui_controls_spec.MenuItemSpec, ...] = (
    gui_controls_spec.MenuItemSpec(
        id=wx.ID_DELETE,
        name="Usuń",
        on_activate_listener_name="on_delete"
    ),
)


class ExportScheduleEntriesDlg(views._base_views.BaseEEnterParamsDlg):

    title: str = "Eksportuj grafik"
    affirmative_btn_label: str = "Eksportuj"

    control_specs = (
        gui_controls_spec.RadioButtonspec(
            identifier="exporter_to_use",
            label="Format:",
            choices=exporters
        ),
    )


add = AddScheduleEntryDlg
listing = SchedulesListing
context_menu_spec = items_list
