from __future__ import annotations

from typing import (
    List,
    Type,
)

import frontend.presenters.base_presenter
import frontend.views.class_rooms
import backend.models.class_room
import backend.models.subject


class ClassRoomsPresenter(frontend.presenters.base_presenter.BasePresenter):

    MODEL_CLASS: Type[
        backend.models.class_room.ClassRoom
    ] = backend.models.class_room.ClassRoom
    view_collections = frontend.views.class_rooms
    all_records: List[backend.models.class_room.ClassRoom]

    def __init__(
        self,
        parent_presenter: frontend.presenters.base_presenter.BasePresenter
    ) -> None:
        super().__init__()
        self.parent_presenter = parent_presenter

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

    @property
    def initial_vals_for_add(self):
        courses_list = [backend.models.class_room.NoMainCourse()]
        courses_list += list(
            backend.models.subject.Subject.from_db(
                self.parent_presenter.focused_entity
            )
        )
        # TODO: Make first item selected and add editing
        return {"PrimaryCourse": courses_list}