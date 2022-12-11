import functools

import wx


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title="Układacz planu zajęć")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)


class PresentationManager:

    def __init__(self) -> None:
        self._active_presenters = []

    def set_initial_presenter(self, presenter):
        self._initial_presenter = presenter

    def present_initial_view(self):
        self.frame_obj = MainFrame()
        wx.GetApp().SetTopWindow(self.frame_obj)
        main_presenter = self._initial_presenter()
        main_presenter.present_all()
        self._active_presenters.append(main_presenter)
        self.frame_obj.Show()





    @property
    def main_window(self) -> MainFrame:
        return self.frame_obj

    def present(self, presenter_to_use):
        self._active_presenters.append(presenter_to_use)
        self._active_presenters[-1].present_all()
        self._active_presenters[-2].hide()
        self.frame_obj.Layout()

    def show_previous_view_if_any(self):
        if len(self._active_presenters) > 1:
            currently_presenting = self._active_presenters[-1]
            should_present = self._active_presenters[-2]
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
