from gi.repository import Gtk, Gdk, Adw

from .timer import CubeTimer


def init_theme():
    settings = Gtk.Settings.get_default()

    prefer_dark_theme = settings.get_property("gtk-application-prefer-dark-theme")

    if prefer_dark_theme:
        return "black"
    else:
        return "white"

    

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/timerlabel.ui')
class CubeTimerLabel(Gtk.Label):
    __gtype_name__ = 'CubeTimerLabel'

    timer = CubeTimer(lambda: None)
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs, focusable = True, can_focus = True)
        self.font_size = 100
        self.set_label()
        self.timer.update_label = self.set_label
        settings = Gtk.Settings.get_default()
        settings.connect("notify::gtk-application-prefer-dark-theme", self.check_theme, None)
        
    def check_theme(self, settings, pspec, user_data):

        prefer_dark_theme = settings.get_property("gtk-application-prefer-dark-theme")
        if prefer_dark_theme:
            self.set_label("white")
        else:
            self.set_label("black")
        

    def set_label(self, color=init_theme()):
        self.set_markup(f"<span font='{self.font_size}' color='{color}'>{self.timer.min:02d}:{self.timer.sec:02d}.{self.timer.milisec:02d}</span>")

