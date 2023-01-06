from __future__ import annotations

import requests

import frontend.presenters.base_presenter
import frontend.views.schedule
import frontend.gui_controls_spec
import backend.models.class_room
import backend.models.subject
import backend.models.class_to_term_plan
import backend.models.teacher
import backend.models.teacher_to_subject
import backend.models.schedule
import backend.models.class_model


class SchedulePresenter(frontend.presenters.base_presenter.BasePresenter):

    is_term_aware = True

    MODEL_CLASS: type[
        backend.models.schedule.Schedule
    ] = backend.models.schedule.Schedule
    view_collections = frontend.views.schedule
    all_records: list[backend.models.schedule.Schedule]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter
        self.for_term = parent_presenter.focused_entity
        self.term_in_inst = self.for_term.owner

    def subjects_in_plan_for_class(self, class_model):
        subjects = list(backend.models.subject.Subject.from_subjects_for_class_endpoint(
            class_model
        ))
        return subjects

    def teachers_allowed_to_teach(self, subject):
        return list(
            backend.models.teacher.Teacher.from_teachers_for_subjs_end_point(
                subject
            )
        )

    def class_rooms_for_subject(self, subject):
        return list(
            backend.models.class_room.ClassRoom.from_class_room_for_subj_end_point(
                subject
            )
        )

    def create_new_entity_from_user_input(self, entered_vals):
        return self.MODEL_CLASS(
            WeekDay=entered_vals["WeekDay"],
            owner=self.term_in_inst,
            ClassId=entered_vals["ClassId"],
            ClassRoomId=entered_vals["ClassRoomId"],
            InTerm=self.for_term,
            LessonEndingHour=entered_vals["LessonEndingHour"],
            LessonStartingHour=entered_vals["LessonStartingHour"],
            TeacherId=entered_vals["TeacherId"],
            SubjectId=entered_vals["SubjectId"]
        )

    def get_possible_ends_for_lesson(
        self,
        class_obj,
        subject_obj,
        start_time
    ):
        query = requests.get(
            "http://127.0.0.1:5000/get_lessons_end_hours",
            params={
                "class_id": class_obj.id,
                "term_id": self.for_term.id,
                "subject_id": subject_obj.id,
                "chosen_lesson_start": start_time
            }
        )
        return query.json()["lesson_ends"]

    def get_possible_week_days_for_lesson(
        self,
        class_obj,
        subject_obj
    ):
        query = requests.get(
            "http://127.0.0.1:5000/get_lesson_preferred_week_day",
            params={
                "class_id": class_obj.id,
                "term_id": self.for_term.id,
                "subject_id": subject_obj.id,
            }
        )
        selection = query.json()["Preferred_day"]
        return frontend.gui_controls_spec.ComboBoxvaluesSpec(
            initial_selection=selection,
            values=list(backend.models.schedule.WeekDay)
        )

    def get_possible_lesson_beginnings(
        self,
        class_obj,
        subject_obj,
        week_day,
        teacher_obj,
        class_room_obj
    ):
        query = requests.get(
            "http://127.0.0.1:5000/get_institutions_lessons",
            params={
                "class_id": class_obj.id,
                "term_id": self.for_term.id,
                "subject_id": subject_obj.id,
                "institution_id": self.term_in_inst.id,
                "week_day": week_day.value,
                "teacher_id": teacher_obj.id,
                "class_room_id": class_room_obj.id
            }
        )
        records = query.json()["lessons"]
        return frontend.gui_controls_spec.ComboBoxvaluesSpec(
            values=records,
            initial_selection=0
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )

    @property
    def initial_vals_for_add(self):
        classes_with_plans = list(
            backend.models.class_model.Class.from_classesToTermPlan_endpoint(
                self.parent_presenter.focused_entity
            )
        )
        combobox_vals = frontend.gui_controls_spec.ComboBoxvaluesSpec(
            values=classes_with_plans,
            initial_selection=0
        )
        return {
            "ClassId": combobox_vals,
        }

    def vals_for_edit(self):
        res = super().vals_for_edit()
        possible_course_choices = self.initial_vals_for_add["PrimaryCourse"]
        chosen_course_id = res["PrimaryCourse"].id 
        for index, course in enumerate(possible_course_choices.values):
            if course.id == chosen_course_id:
                possible_course_choices.initial_selection = index
                break
        res["PrimaryCourse"] = possible_course_choices
        return res
