from __future__ import annotations

from typing import (
    List,
    Type,
)

import presenters.base_presenter
import presentation_manager
import views.class_rooms
import gui_controls_spec
import models.class_room
import models.institution
import models.subject
import presenters.schedule_presenter


class ClassRoomsPresenter(presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        models.class_room.ClassRoom
    ] = models.class_room.ClassRoom
    view_collections = views.class_rooms
    all_records: List[models.class_room.ClassRoom]
    detail_presenters = (presenters.schedule_presenter.SchedForClassRoomPres,)

    @property
    def owning_inst(self) -> models.institution.Institution:
        return presentation_manager.get_presentation_manager()._active_presenters[-2].focused_entity

    def on_new_term_selected(self, term_obj):
        if term_obj is None:
            return
        self.det.for_term = term_obj
        self.det.term_in_inst = self.det.for_term.owner
        self.det.populate_on_change()

    def master_item_changed(self, index):
        self.det.class_room =  self.all_records[index]
        self.det.populate_on_change()

    def handle_detail_presenter(self, detail_pres):
        self.det = detail_pres
        try:
            self.det.class_room =  self.focused_entity
        except RuntimeError:  # Empty list - we cannot continue in that case
            pass
        c = None
        for c in detail_pres.conts:
            if c.identifier == "terms":
                break
        if c is None:
            raise RuntimeError
        c.register_to_changes(self.on_new_term_selected)
        c.set_value(
            gui_controls_spec.ComboBoxvaluesSpec(
                list(self.owning_inst.terms_in_inst()),
                initial_selection=0
            )
        )
        self.p.on_item_focused_listeners.append(self.master_item_changed)

    def create_new_entity_from_user_input(self, entered_vals):
        entered_vals[self.MODEL_CLASS.fk_field_name()] = self.owning_inst
        return self.MODEL_CLASS.from_normalized_record(entered_vals)

    def get_all_records(self):
        yield from self.MODEL_CLASS.from_endpoint(self.owning_inst)

    @property
    def initial_vals_for_add(self):
        courses_list = [models.class_room.NoMainCourse()]
        courses_list += list(
            models.subject.Subject.from_endpoint(
                self.owning_inst
            )
        )
        combobox_vals = gui_controls_spec.ComboBoxvaluesSpec(
            values=courses_list,
            initial_selection=0
        )
        return {"PrimaryCourse": combobox_vals}

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
