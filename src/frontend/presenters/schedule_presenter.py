from __future__ import annotations

import requests

import presenters.base_presenter
import views.schedule
import gui_controls_spec
import backend.models.class_room
import backend.models.subject
import backend.models.class_to_term_plan
import backend.models.teacher
import backend.models.teacher_to_subject
import backend.models.schedule
import backend.models.class_model


class SchedulePresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: type[
        backend.models.schedule.Schedule
    ] = backend.models.schedule.Schedule
    view_collections = views.schedule
    all_records: list[backend.models.schedule.Schedule]

    def get_controls_for_secondary_view(self):
        self.terms_list = gui_controls_spec.LabeledComboBoxSpec(
            identifier="terms",
            label="Semestry:",
        )
        yield self.terms_list

    def present_as_detail(self, master_presenter)-> None:
        self.conts = []
        for c in self.get_controls_for_secondary_view():
            res = c.create(master_presenter)
            res.add_to_sizer(master_presenter.main_sizer)
            self.conts.append(res)

    def subjects_in_plan_for_class(self, class_model):
        subjects = list(backend.models.subject.Subject.from_subjects_for_class_endpoint(
            class_model
        ))
        return subjects

    def teachers_allowed_to_teach(self, subject):
        if subject is None:
            return []
        return list(
            backend.models.teacher.Teacher.from_teachers_for_subjs_end_point(
                subject
            )
        )

    def class_rooms_for_subject(self, subject):
        if subject is None:
            return []
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
        return gui_controls_spec.ComboBoxvaluesSpec(
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
        return gui_controls_spec.ComboBoxvaluesSpec(
            values=records,
            initial_selection=0
        )

    def get_all_records(self):
        return []

    @property
    def initial_vals_for_add(self):
        classes_with_plans = list(
            backend.models.class_model.Class.from_classesToTermPlan_endpoint(
                self.for_term
            )
        )
        combobox_vals = gui_controls_spec.ComboBoxvaluesSpec(
            values=classes_with_plans,
            initial_selection=0
        )
        return {
            "ClassId": combobox_vals,
        }



class SchedForClassRoomPres(SchedulePresenter):

    def get_all_records_for_detail(self):
        yield from self.MODEL_CLASS.entries_in_class_room(term=self.for_term, class_room=self.class_room)

    def populate_on_change(self):
        while True:
            if not self.p.list_ctrl.DeleteItem(0):
                break
        for record in self.get_all_records_for_detail():
            self._present_single_in_view(record)
        self.p.list_ctrl.Select(0)
        self.p.list_ctrl.Focus(0)
        self.set_toolbar_icons_state()


class SchedForTeacherPres(SchedForClassRoomPres):

    def get_all_records_for_detail(self):
        yield from self.MODEL_CLASS.entries_for_teacher(term=self.for_term, teacher=self.teacher)


class SchedForClassPres(SchedForClassRoomPres):

    def get_all_records_for_detail(self):
        yield from self.MODEL_CLASS.entries_for_class(term=self.for_term, class_model=self.class_mod)
