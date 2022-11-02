import wx

import frontend.gui_controls_spec as ctrl_specs


def wx_button_factory(
        ctrl_parent: wx.Window,
        control_params: ctrl_specs.WXButtonSpec
) -> wx.Button:
    btn = wx.Button(ctrl_parent, label=control_params.label)
    btn.Bind(wx.EVT_BUTTON, control_params.on_press)
    return btn
