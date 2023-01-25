from __future__ import annotations

import requests

import presenters.base_presenter
import views.schedule
import gui_controls_spec
import models.class_room
import models.subject
import models.class_to_term_plan
import models.teacher
import models.teacher_to_subject
import models.schedule
import models.class_model
import api_utils


class SchedulePresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: type[
        models.schedule.Schedule
    ] = models.schedule.Schedule
    view_collections = views.schedule
    all_records: list[models.schedule.Schedule]

    def on_export(self):
        entries_ids_to_export = [_.id for _ in self.all_records]
        export_dlg = self.view_collections.ExportScheduleEntriesDlg(parent=self.p)
        with export_dlg as dlg:
            if dlg.ShowModal() == dlg.AffirmativeId:
                selected_exporter = dlg.get_values()["exporter_to_use"]
                exported_content = api_utils.post_data(
                    end_point_name=selected_exporter.export_end_point,
                    json_data={
                        "lesson_ids": entries_ids_to_export,
                    }
                )
                selected_exporter.do_export(self.p, exported_content.text)

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
        subjects = list(models.subject.Subject.from_subjects_for_class_endpoint(
            class_model
        ))
        return subjects

    def teachers_allowed_to_teach(self, subject):
        if subject is None:
            return []
        return list(
            models.teacher.Teacher.from_teachers_for_subjs_end_point(
                subject
            )
        )

    def class_rooms_for_subject(self, subject):
        if subject is None:
            return []
        return list(
            models.class_room.ClassRoom.from_class_room_for_subj_end_point(
                subject
            )
        )

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.term_in_inst
        entered_vals["InTerm"] = self.for_term
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

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
            values=list(models.schedule.WeekDay)
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
            models.class_model.Class.from_classesToTermPlan_endpoint(
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
        try:
            yield from self.MODEL_CLASS.entries_in_class_room(term=self.for_term, class_room=self.class_room)
        except AttributeError:
            return []

    def populate_on_change(self):
        self.all_records.clear()
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
        try:
            yield from self.MODEL_CLASS.entries_for_teacher(term=self.for_term, teacher=self.teacher)
        except AttributeError:
            return []


class SchedForClassPres(SchedForClassRoomPres):

    def get_all_records_for_detail(self):
        try:
            yield from self.MODEL_CLASS.entries_for_class(term=self.for_term, class_model=self.class_mod)
        except AttributeError:
            return []
