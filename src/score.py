from gi.repository import Gtk, GLib, GObject, Gio, Adw, Pango
from .utils import calc_time, time_string
import os
import json
from pathlib import Path

data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'flatpak' / 'apps' / 'cube-timer' / 'CubeTimer'
data_dir.mkdir(parents=True, exist_ok=True)
scores_file_path = data_dir / 'scores.json'

class CubeTimerModel:
    def __init__(self):
        self.path = scores_file_path
        self.sessions = {"Session 1": []}
        self.load()

    def load(self):
        # for backward compatibility
        def modscore(score):
            if "min" not in score:
                return score
            score["time"] = score["min"] * 6000 + score["sec"] * 100 + score["mili"]
            score.pop("min", None)
            score.pop("sec", None)
            score.pop("mili", None)
            score.pop("ao5", None)
            score.pop("ao12", None)
            return score

        try:
            with open(self.path, 'r') as scores_file:
                sessions = json.load(scores_file)
                for session in sessions:
                    for score in sessions[session]:
                        self.sessions[session].append(modscore(score))
        except FileNotFoundError:
            print("scores.json not found.")
            self.sessions = {"Session 1": []}

        self.save()

    def save(self):
        with open(self.path, "w") as scores_file:
            json.dump(self.sessions, scores_file)

    def get_session(self, session):
        return self.sessions[session]

    def get_score(self, session, index):
        return self.sessions[session][index]

    def add_score(self, session, score):
        self.sessions[session].append(score)
        self.save()

    def delete_score(self, session, index):
        self.sessions[session].pop(index)
        self.save()

    def dnf_score(self, session, index):
        self.sessions[session][index]["time"] = 0
        self.save()

    def calculate_average(self, session, index, n):
        index = index if index != -1 else len(self.sessions[session])-1

        if index + 1 < n:
            return -1

        avg = 0
        dnf = 0
        for i in range(index, index-n, -1):
            dnf += (self.sessions[session][i]["time"] == 0)
            avg += self.sessions[session][i]["time"]

        if dnf > n // 2:
            return 0

        avg //= (n - dnf)
        return avg

class Scores(GObject.Object):
    index: int = GObject.Property(type=int)

    def __init__(self, index: int):
        super().__init__()
        self.index = index

class Session(GObject.Object):
    name: str = GObject.Property(type=str)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

@Gtk.Template(resource_path='/io/github/vallabhvidy/CubeTimer/score.ui')
class ScoresColumnView(Gtk.ScrolledWindow):
    __gtype_name__ = "ScoresColumnView"

    scores_column_view = Gtk.Template.Child()
    dialog = Gtk.Template.Child()
    time_row = Gtk.Template.Child()
    scramble_row = Gtk.Template.Child()

    def __init__(self):

        self.model = CubeTimerModel()
        self.current_session = "Session 1"
        self.store = Gio.ListStore()
        self.select = Gtk.SingleSelection()
        self.selected_index = 0

        self.build_column_view()
        self.build_dialog()

        self.load_scores(self.current_session)

    def build_column_view(self):
        self.select.set_model(self.store)
        self.scores_column_view.set_model(self.select)

        fact1 = Gtk.SignalListItemFactory()
        fact2 = Gtk.SignalListItemFactory()
        fact3 = Gtk.SignalListItemFactory()
        fact4 = Gtk.SignalListItemFactory()

        def f_setup(fact, item):
            label = Gtk.Label(halign=Gtk.Align.START)
            label.set_selectable(False)
            item.set_child(label)

        fact1.connect("setup", f_setup)
        fact2.connect("setup", f_setup)
        fact3.connect("setup", f_setup)
        fact4.connect("setup", f_setup)

        def f_bind1(fact, item):
            item.get_child().set_label(str(item.get_item().index+1))

        def f_bind2(fact, item):
            score = self.model.get_score(self.current_session, item.get_item().index)
            item.get_child().set_label(time_string(score["time"]))

        def f_bind3(fact, item):
            ao5 = time_string(self.model.calculate_average(self.current_session, item.get_item().index, 5))
            item.get_child().set_label(ao5)

        def f_bind4(fact, item):
            ao12 = time_string(self.model.calculate_average(self.current_session, item.get_item().index, 12))
            item.get_child().set_label(ao12)

        fact1.connect("bind", f_bind1)
        fact2.connect("bind", f_bind2)
        fact3.connect("bind", f_bind3)
        fact4.connect("bind", f_bind4)

        col1 = Gtk.ColumnViewColumn(title=_("Sr."), factory=fact1)
        col2 = Gtk.ColumnViewColumn(title=_("Time"), factory=fact2)
        col3 = Gtk.ColumnViewColumn(title=_("ao5"), factory=fact3)
        col4 = Gtk.ColumnViewColumn(title=_("ao12"), factory=fact4)

        col1.set_fixed_width(35)
        col2.set_fixed_width(80)
        col3.set_fixed_width(80)
        col4.set_fixed_width(80)

        self.scores_column_view.append_column(col1)
        self.scores_column_view.append_column(col2)
        self.scores_column_view.append_column(col3)
        self.scores_column_view.append_column(col4)

        self.scores_column_view.connect("activate", self.on_click)

    def build_dialog(self):
        def on_response(widget, response):
            if response == 'delete':
                self.delete_index(self.selected_index)
            elif response == "dnf":
                self.dnf_index(self.selected_index)

        self.dialog.add_response("dnf", _("Mark DNF"))
        self.dialog.add_response("delete", _("Delete"))
        self.dialog.add_response("cancel", _("Cancel"))

        self.dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        self.dialog.set_response_appearance("dnf", Adw.ResponseAppearance.SUGGESTED)
        self.dialog.connect('response', on_response)

    def scroll_to_bottom(self):
        vadj = self.get_vadjustment()
        GLib.timeout_add(30, lambda: (vadj.set_value(vadj.get_upper()) and False))

    def add_score(self, time, scramble):
        score = {"time": time+1, "scramble": scramble}
        self.model.add_score(self.current_session, score)
        self.store.append(Scores(len(self.store)))
        self.select.set_selected(len(self.store)-1)
        self.scroll_to_bottom()

    def on_click(self, widget, index):
        item = self.model.get_score(self.current_session, index)
        self.selected_index = index

        time = time_string(item['time'])
        scramble = item['scramble']
        alert_string = _("Scramble:- {scramble}\n\nTime:- {time}").format(scramble=scramble, time=time)

        self.dialog.set_heading(_("Solve No. {idx}").format(idx=index+1))
        self.time_row.set_label(time)
        self.scramble_row.set_title(scramble)

        self.dialog.present(self)

    def delete_index(self, index):
        self.model.delete_score(self.current_session, index)

        while index < len(self.store):
            self.store.remove(index)

        for idx in range(index, len(self.model.get_session(self.current_session))):
            self.store.append(Scores(idx))

    def dnf_index(self, index):
        self.model.dnf_score(self.current_session, index)

        while index < len(self.store):
            self.store.remove(index)

        for idx in range(index, len(self.model.get_session(self.current_session))):
            self.store.append(Scores(idx))

    def load_scores(self, session):
        for idx in range(len(self.model.get_session(session))):
            self.store.append(Scores(idx))

