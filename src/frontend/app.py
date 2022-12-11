import wx

import frontend.presenters.institutions_presenter
import frontend.presentation_manager


def main() -> None:
    app = wx.App(False)
    pm = frontend.presentation_manager.get_presentation_manager()
    pm.set_initial_presenter(
        frontend.presenters.institutions_presenter.InstitutionPresenter
    )
    pm.present_initial_view()
    app.MainLoop()
