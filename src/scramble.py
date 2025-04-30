from gi.repository import Gtk

from random import randint

moves = ['U', 'D', 'R', 'L', 'F', 'B']
direction = ['', "'", "2"]
number = 25

def scramble_gen(scramble_length):
    arr = [[0, 0] for _ in range(scramble_length)]
    arr[0][0] = moves[randint(0, 5)]
    arr[0][1] = direction[randint(0, 2)]
    i = 1
    while(i < scramble_length):
        arr[i][0] = moves[randint(0, 5)]
        arr[i][1] = direction[randint(0, 2)]
        if arr[i-1][0] == arr[i][0]:
            continue
        i += 1
    scramble = " ".join([a[0]+a[1] for a in arr])
    return scramble

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
