import wx

import frontend.presentation_manager


def main() -> None:
    app = wx.App(False)
    frontend.presentation_manager.get_presentation_manager()
    app.MainLoop()
