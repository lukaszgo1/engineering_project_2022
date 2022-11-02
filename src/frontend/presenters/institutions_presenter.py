from __future__ import annotations

import backend.models.institution
import frontend.views.institutions.listing


class InstitutionPresenter:

    MODEL_CLASS = backend.models.institution.Institution
    view_collections = frontend.views.institutions

    def __init__(
        self,
        tmp_panel: frontend.views.institutions.listing.InstitutionsListing
    ) -> None:
        self.p = tmp_panel
        self.all_records = list()

    def _present_single_in_view(self, to_show: MODEL_CLASS) -> None:
        col_values = []
        for column_info in self.p.list_view_columns:
            col_value = column_info.value_getter(to_show)
            if(
                column_info.value_converter
                and callable(column_info.value_converter)
            ):
                col_value = column_info.value_converter(col_value)
            col_values.append(col_value)
        self.p.list_ctrl.Append(col_values)

    def present_all(self):
        for record in self.MODEL_CLASS.from_db():
            self.all_records.append(record)
            self._present_single_in_view(record)
