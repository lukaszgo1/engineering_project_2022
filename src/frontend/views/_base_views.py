from typing import (
    Callable,
    Dict,
    List,
    Tuple,
)

import wx

import frontend.gui_control_factories as factories
import frontend.gui_controls_spec as ctrl_specs


class BaseEntityList(wx.Panel):

    buttons_in_view: List[ctrl_specs.WXButtonSpec]
    list_view_columns: List[ctrl_specs.WXListColumnSpec]
    on_item_focused_listeners: List[Callable[[int], None]]

    def __init__(self, presenter) -> None:  # TODO: add type hint
        self.on_item_focused_listeners = []
        self.presenter = presenter
        self_context_menu_pos = None
        super().__init__(wx.GetApp().TopWindow)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_ctrl = wx.ListCtrl(
            self,
            size=(-1, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL
        )
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.on_context)
        self.list_ctrl.Bind(
            wx.EVT_LIST_ITEM_FOCUSED,
            self.on_new_item_focused
        )
        self._create_list_columns()
        self.list_ctrl.Bind(wx.EVT_KEY_UP, self.on_key_pressed)
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)
        for btn in self.buttons_in_view:
            main_sizer.Add(
                factories.wx_button_factory(
                    ctrl_parent=self,
                    control_params=btn
                ),
                0,
                wx.ALL | wx.CENTER,
                5
            )
        self.SetSizer(main_sizer)

    def on_key_pressed(self, event):
        if event.KeyCode == wx.WXK_ESCAPE:
            self.presenter.show_previous_view()

    def focus_list(self):
        self.list_ctrl.SetFocus()

    def on_context(self, event: wx.ContextMenuEvent) -> None:
        if not self.presenter.any_focused:
            return
        menu_pos: wx.Point = event.GetPosition()
        if not menu_pos.IsFullySpecified():
            # Menu opened from the keyboard 
            # calculate the suitable position based on the focused list item
            focused_item_pos = self.list_ctrl.GetItemPosition(
                self.list_ctrl.FocusedItem
            )
            menu_pos = focused_item_pos
        menu = self.presenter.show_context_menu_for_entity()
        self.PopupMenu(menu, menu_pos)

    def on_new_item_focused(self, event: wx.ListEvent) -> None:
        new_focused_index = event.Index
        for listener in self.on_item_focused_listeners:
            listener(new_focused_index)

    def _create_list_columns(self) -> None:
        for col_index, list_col in enumerate(self.list_view_columns):
            self.list_ctrl.InsertColumn(
                col_index,
                list_col.header_name,
                width=list_col.width
            )

    def record_cols_to_presentable_form(self, record):
        col_values = []
        for column_info in self.list_view_columns:
            col_value = column_info.value_getter(record)
            if (
                column_info.value_converter
                and callable(column_info.value_converter)
            ):
                col_value = column_info.value_converter(col_value)
            col_values.append(col_value)
        return col_values

    def add_new_item(self, item_to_add, should_focus: bool = False) -> int:
        self.list_ctrl.Append(
            self.record_cols_to_presentable_form(item_to_add)
        )
        if should_focus:
            # Unselect the currently selected items if any.
            sel_index = self.list_ctrl.GetFirstSelected()
            while sel_index >= 0:
                self.list_ctrl.Select(sel_index, on=0)
                sel_index = self.list_ctrl.GetNextSelected(sel_index)
            new_entry_index = self.list_ctrl.ItemCount - 1
            self.list_ctrl.Select(new_entry_index)
            self.list_ctrl.Focus(new_entry_index)
            self.list_ctrl.SetFocus()
        return self.list_ctrl.ItemCount - 1

    def update_shown_entity(self, new_entity, entity_index: int) -> None:
        presentable_vals = self.record_cols_to_presentable_form(new_entity)
        for col_index in range(self.list_ctrl.ColumnCount):
            self.list_ctrl.SetItem(
                entity_index,
                col_index,
                presentable_vals[col_index]
            )

    def delete_item(self, index: int) -> None:
        self.list_ctrl.DeleteItem(index)
        self.list_ctrl.SetFocus()

    def show(self):
        wx.GetApp().TopWindow.sizer.Add(self, 1, wx.EXPAND)
        self.Show()


class BaseEEnterParamsDlg(wx.Dialog):

    title: str
    added_controls: List[factories._base_control]
    control_specs: Tuple[ctrl_specs._ControlWrapperBase, ...]
    affirmative_btn_label: str
    cancel_btn_label: str = "Anuluj"

    def __init__(self, parent: wx.Window, presenter=None) -> None:
        self.added_controls = []
        self.presenter = presenter
        super().__init__(parent=parent, title=self.title)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.helper_sizer = wx.BoxSizer(wx.VERTICAL)
        self._on_change_listeners = list()
        for control_spec in self.control_specs:
            control = control_spec.create(self)
            control.add_to_sizer(self.helper_sizer)
            self.added_controls.append(control)
            if control_spec.on_change_notifier is not None:
                listener = control_spec.on_change_notifier(
                    self.presenter, control
                )
                self._on_change_listeners.append(listener)
        for listening_control in self._on_change_listeners:
            for ct, ct_spec in zip(self.added_controls, self.control_specs):
                if ct_spec.should_react_to_changes:
                    listening_control.add_dependend_control(ct)
        self.main_sizer.Add(
            self.helper_sizer,
            border=20,
            flag=wx.LEFT | wx.RIGHT | wx.TOP
        )
        btn_sizer = wx.BoxSizer()
        affirmative_btn = wx.Button(self, label=self.affirmative_btn_label)
        self.SetAffirmativeId(affirmative_btn.Id)
        affirmative_btn.SetDefault()
        btn_sizer.Add(affirmative_btn, 0, wx.ALL, 5)
        cancel_btn = wx.Button(self, label=self.cancel_btn_label)
        self.SetEscapeId(cancel_btn.Id)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.main_sizer.Fit(self)
        self.SetSizer(self.main_sizer)

    def set_values(self, vals_to_set: Dict) -> None:
        for control in self.added_controls:
            if control.identifier in vals_to_set:
                control.set_value(vals_to_set[control.identifier])

    def get_values(self) -> Dict:
        cols_to_vals = dict()
        for cont in (c for c in self.added_controls if c.is_enabled):
            cols_to_vals.update(cont.get_value())
        return cols_to_vals
