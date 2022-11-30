import functools

import wx

import frontend.presenters.institutions_presenter

initial_pres = frontend.presenters.institutions_presenter.InstitutionPresenter


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title="Układacz planu zajęć")
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)


class PresentationManager:

    def __init__(self) -> None:
        self.frame_obj = MainFrame()
        self._active_presenters = []
        wx.GetApp().SetTopWindow(self.frame_obj)
        main_presenter = initial_pres()
        self._active_presenters.append(main_presenter)
        main_presenter.present_all()
        self.frame_obj.Show()


@functools.lru_cache(maxsize=1)
def get_presentation_manager():
    return PresentationManager()
