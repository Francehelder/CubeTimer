from gi.repository import Gtk
from .utils import scramble_gen

number = 20

class Scramble(Gtk.Label):
    __gtype_name__ = 'Scramble'

    def __init__(self, **kargs):
        self.scramble = scramble_gen(number)
        self.set_text(self.scramble)

    def update_scramble(self):
        self.scramble = scramble_gen(number)
        self.set_text(self.scramble)

    def show_scramble(self):
        self.set_visible(True)

    def hide_scramble(self):
        self.set_visible(False)


if __name__ == "__main__":
    print(scramble_gen(int(input(_("Enter scramble length:- ")))))
