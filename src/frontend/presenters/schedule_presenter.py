from __future__ import annotations

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

    MODEL_CLASS: type[
        backend.models.class_room.ClassRoom
    ] = backend.models.class_room.ClassRoom
    view_collections = frontend.views.schedule
    all_records: list[backend.models.class_room.ClassRoom]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

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
            ClassRoomIdentifier=entered_vals["ClassRoomIdentifier"],
            MainSubjectId=entered_vals["PrimaryCourse"].id,
            PrimaryCourse=entered_vals["PrimaryCourse"],
            owner=self.parent_presenter.focused_entity
        )

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_db(
            self.parent_presenter.focused_entity
        )

    def add_new_entry(self):
        return super().add_new_entry()

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
        week_days = list(backend.models.schedule.WeekDay)
        return {
            "ClassId": combobox_vals,
            "WeekDay": frontend.gui_controls_spec.ComboBoxvaluesSpec(week_days),
            "LessonStartingHour": frontend.gui_controls_spec.ComboBoxvaluesSpec(
                [_.strftime("%H:%M") for _ in self.parent_presenter.focused_entity.owner.lessons()]
            )
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
