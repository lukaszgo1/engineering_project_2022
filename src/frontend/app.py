import wx

import presenters.institutions_presenter
import presentation_manager


def main() -> None:
    app = wx.App(False)
    pm = presentation_manager.get_presentation_manager()
    pm.set_initial_presenter(
        presenters.institutions_presenter.InstitutionPresenter
    )
    pm.present_initial_view()
    app.MainLoop()


if __name__ == "__main__":
    main()
