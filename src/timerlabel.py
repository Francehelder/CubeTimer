from gi.repository import Gtk, Gdk, Adw

from .timer import CubeTimer
from .utils import time_string

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/timerlabel.ui')
class CubeTimerLabel(Gtk.Label):
    __gtype_name__ = 'CubeTimerLabel'

    timer = CubeTimer(lambda: None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs, focusable = True, can_focus = True)
        self.font_size = 100
        self.color = "white" if Adw.StyleManager.get_default().get_color_scheme() == Adw.ColorScheme.PREFER_DARK else "black"
        self.set_color()
        self.set_label()
        self.timer.update_label = self.set_label
        settings = Gtk.Settings.get_default()
        settings.connect("notify::gtk-application-prefer-dark-theme", self.theme_change)
        
    def theme_change(self, source, pspec):
        self.set_color()

    def set_color(self):
        self.color = "white" if self.color == "black" else "black"
        self.set_label()

    def set_label(self, color=None):
        color = self.color if color == None else color
        time = time_string(self.timer.time)
        time = time if time != "DNF" else "00:00.00"
        time_format = _("<span color='{color}'>{time}</span>")
        self.set_markup(time_format.format(
            color=color,
            time=time
        ))

