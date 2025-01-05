from gi.repository import Adw
from gi.repository import Gtk, GLib, GObject
from time import time

state: bool = True

delay = 0.20

def check_theme():
        style_manager = Adw.StyleManager.get_default()
        scheme = style_manager.get_color_scheme()
        
        if scheme == style_manager.get_dark():
            return "black"
        else:
            return "white"

class CubeTimer(GObject.Object):
    __gtype_name__ = 'CubeTimer'

    def __init__(self, update_label, **kwargs):
        super().__init__(**kwargs)
        self.min = 0
        self.sec = 0
        self.milisec = 0
        self.timer_running = False
        self.space_pressed = False
        self.space_released = True
        self.update_label = update_label
        self.update_scores = None
        self.scramble = None
        self.get_set = False
        self.sidebar_button = None
        self.split_view_state: bool = True

    def start_timer(self):
        self.timer_running = True
        self.update_label(check_theme())
        self.prev_time = time()
        self.acc_check_1 = self.prev_time
        GLib.timeout_add(1, self.update_timer)

    # def update_timer(self):
    #     if (self.timer.elapsed() == 1):
    #         self.sec += 1
    #     if (self.sec == 60):
    #         self.min += 1
    #         self.sec = 0
    #     if self.timer_running:
    #         self.update_timer()
    #     else:
    #         self.timer.stop()
    #         return False

    def update_timer(self):
        if round(time() - self.prev_time > 0.01):
            self.prev_time = time()
            self.milisec += 1
            if self.milisec == 100:
                self.sec += 1
                self.milisec = 0
            if self.sec == 60:
                self.min += 1
                self.sec = 0
            self.update_label(check_theme())
        if self.timer_running:
            GLib.timeout_add(1, self.update_timer)
        else:
            return False

    def stop_timer(self):
        self.scramble.show_scramble()
        self.sidebar_button.set_visible(True)
        self.timer_running = False
        print((time()-self.acc_check_1)*1000)
        self.split_view.set_show_sidebar(state)
        self.update_scores(f"{self.min:02d}:{self.sec:02d}.{self.milisec:02d}", self.min, self.sec, self.milisec, self.scramble.scramble)

    def key_press(self, event, keyval, keycode, state):
        if keyval == ord(' '):
            if not self.timer_running and not self.space_pressed:
                self.update_label("red")
                self.space_pressed = True
                self.space_pressed_time = time()
            elif self.timer_running:
                self.stop_timer()
            elif self.space_pressed:
                if time() - self.space_pressed_time >= delay:
                    self.reset_timer()
                    state = bool(self.split_view.get_show_sidebar())
                    # print(state)
                    self.split_view.set_show_sidebar(False)
                    # print(state)
                    self.scramble.hide_scramble()
                    self.sidebar_button.set_visible(False)
                    self.update_label("green")
                    self.get_set = True
        elif self.timer_running:
            self.stop_timer()

    def key_released(self, event, keyval, keycode, state):
        if self.space_pressed:
            if self.get_set:
                self.start_timer()
                self.scramble.update_scramble()
                self.get_set = False
            self.space_pressed = False
            self.update_label(check_theme())

    def reset_timer(self):
        self.min = self.sec = self.milisec = 0




