from typing import (
    List,
)

import wx

import frontend.gui_control_factories as factories
import frontend.gui_controls_spec as ctrl_specs


class BaseEntityList(wx.Panel):

    buttons_in_view: List[ctrl_specs.WXButtonSpec]
    list_view_columns: List[ctrl_specs.WXListColumnSpec]

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_ctrl = wx.ListCtrl(
            self,
            size=(-1, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.on_context)
        self._create_list_columns()
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

    def on_context(self, event: wx.ContextMenuEvent) -> None:
        print(type(event))

    def _create_list_columns(self) -> None:
        for col_index, list_col in enumerate(self.list_view_columns):
            self.list_ctrl.InsertColumn(
                col_index,
                list_col.header_name,
                width=list_col.width
            )
