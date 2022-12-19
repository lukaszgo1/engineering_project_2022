import functools

import wx

import frontend.gui_controls_spec


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title="Układacz planu zajęć")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.toolbar_obj: wx.ToolBar = self.CreateToolBar(style=wx.TB_TEXT | wx.TB_HORIZONTAL)


class PresentationManager:

    def __init__(self) -> None:
        self._active_presenters = []
        self.toolbar_ids_to_items: dict[int, frontend.gui_controls_spec.ToolBarItemSpec] = dict()

    def on_toolbar_item_clicked(self, event):
        self.toolbar_ids_to_items[event.Id].click()

    def set_initial_presenter(self, presenter):
        self._initial_presenter = presenter

    def populate_toolbar(
        self,
        items: list[frontend.gui_controls_spec.ToolBarItemSpec]
    ) -> None:
        self.frame_obj.toolbar_obj.ClearTools()
        self.toolbar_ids_to_items.clear()
        for item in items:
            self.frame_obj.toolbar_obj.AddTool(
                item.item_id,
                item.label,
                item.bitmap
            )
            self.toolbar_ids_to_items[item.item_id] = item
        self.frame_obj.toolbar_obj.Realize()

    def present_initial_view(self):
        self.frame_obj = MainFrame()
        self.frame_obj.toolbar_obj.Bind(wx.EVT_TOOL, self.on_toolbar_item_clicked)
        wx.GetApp().SetTopWindow(self.frame_obj)
        main_presenter = self._initial_presenter()
        self.populate_toolbar(list(main_presenter.toolbar_items()))
        main_presenter.present_all()
        self._active_presenters.append(main_presenter)
        self.frame_obj.Show()

    @property
    def main_window(self) -> MainFrame:
        return self.frame_obj

    def present(self, presenter_to_use):
        self._active_presenters.append(presenter_to_use)
        self._active_presenters[-1].present_all()
        self.populate_toolbar(list(self._active_presenters[-1].toolbar_items()))
        self._active_presenters[-2].hide()
        self.frame_obj.Layout()

    def show_previous_view_if_any(self):
        if len(self._active_presenters) > 1:
            currently_presenting = self._active_presenters[-1]
            should_present = self._active_presenters[-2]
            self.populate_toolbar(list(should_present.toolbar_items()))
            del self._active_presenters[-2]
            del self._active_presenters[-1]
            self.frame_obj.sizer.Remove(0)
            should_present.present_all()
            currently_presenting.hide()
            self._active_presenters.append(should_present)
            self.frame_obj.Layout()


@functools.lru_cache(maxsize=1)
def get_presentation_manager() -> PresentationManager:
    return PresentationManager()
