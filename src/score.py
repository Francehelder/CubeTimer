from gi.repository import Gtk, GLib, GObject, Gio, Adw
import os
import json
from pathlib import Path

data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'flatpak' / 'apps' / 'cube-timer' / 'CubeTimer'
data_dir.mkdir(parents=True, exist_ok=True)
scores_file_path = data_dir / 'scores.json'


class Scores(GObject.Object):
    index: int = GObject.Property(type=int)
    time: str = GObject.Property(type=str)
    ao5: str = GObject.Property(type=str)
    ao12: str = GObject.Property(type=str)

    def __init__(self, index: int, time: str, ao5: str, ao12: str):
        super().__init__()
        self.index = index
        self.time = time
        self.ao5 = ao5
        self.ao12 = ao12

class Session(GObject.Object):
    name: str = GObject.Property(type=str)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

class ScoresColumnViewBox(Gtk.Box):
    __gtype_name__ = "ScoresColumnViewBox"

    def __init__(self):
        # print(scores_file_path)
        self.scores = dict()
        self.scores_column_view = Gtk.ColumnView()
        self.store = Gio.ListStore()
        self.main_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 6)
        self.sub_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 6)
        self.sub_box.set_homogeneous(False)
        # self.append(self.main_box)
        self.append(self.scores_column_view)
        self.dropdown = Gtk.DropDown.new()
        self.dropdown.set_hexpand(True)
        self.main_box.append(self.sub_box)
        self.sub_box.append(self.dropdown)
        self.button = Gtk.Button.new_from_icon_name("list-add")
        self.delete = Gtk.Button.new_from_icon_name("list-remove")
        self.button.connect("clicked", self.on_clicked)
        self.delete.connect("clicked", self.on_delete)
        self.sub_box.append(self.button)
        self.sub_box.append(self.delete)
        # self.main_box.append(self.scores_column_view)
        ss = Gtk.SingleSelection()
        ss.set_model(self.store)
        self.scores_column_view.set_model(ss)

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
            item.get_child().set_label(str(item.get_item().index))

        def f_bind2(fact, item):
            item.get_child().set_label(item.get_item().time)

        def f_bind3(fact, item):
            item.get_child().set_label(item.get_item().ao5)

        def f_bind4(fact, item):
            item.get_child().set_label(item.get_item().ao12)

        fact1.connect("bind", f_bind1)
        fact2.connect("bind", f_bind2)
        fact3.connect("bind", f_bind3)
        fact4.connect("bind", f_bind4)

        col1 = Gtk.ColumnViewColumn(title=_("Sr."), factory=fact1)
        col2 = Gtk.ColumnViewColumn(title=_("Time"), factory=fact2)
        col3 = Gtk.ColumnViewColumn(title=_("ao5"), factory=fact3)
        col4 = Gtk.ColumnViewColumn(title=_("ao12"), factory=fact4)

        col1.set_fixed_width(25)
        col2.set_fixed_width(75)
        col3.set_fixed_width(75)
        col4.set_fixed_width(75)

        self.scores_column_view.append_column(col1)
        self.scores_column_view.append_column(col2)
        self.scores_column_view.append_column(col3)
        self.scores_column_view.append_column(col4)

        self.fetch_scores()
        self.load_session_init()
        self.load_scores(self.current_session)

        self.dropdown.connect('notify::selected', self.on_session_changed)

        self.scores_column_view.set_single_click_activate(True)
        self.scores_column_view.connect("activate", self.on_click)

    def on_click(self, widget, index):
        def on_response(widget, response):
            if response == 'delete':
                self.delete_index(index)
            elif response == "dnf":
                self.dnf_index(index)

        item = self.scores[self.current_session][index]
        alert = Adw.AlertDialog.new(_(f"Solve No. {index + 1}"), _(f"Scramble:- {item.get('scramble')}\n\nTime:- {item.get('time')}"))
        alert.add_response("dnf", _("Mark DNF"))
        alert.add_response("delete", _("Delete"))
        alert.add_response("cancel", _("Cancel"))
        alert.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        alert.present()
        alert.connect('response', on_response)

    def delete_index(self, index):
        self.scores[self.current_session].pop(index)
        select = self.scores_column_view.get_model()
        model = select.get_model()
        # model.remove(index)
        # for i in range(1, len(model)+1):
        #     model[i-1].index = i

        l = len(model)
        temp = []
        for i in range(index + 1, l):
            temp.append(Scores(i, model[i].time, model[i].ao5, model[i].ao12))

        for i in range(index, l):
            model.remove(index)

        i = index
        j = 0
        while i < len(temp) + index and j < 5:
            item = self.scores[self.current_session][i]
            min, sec, mili = item['min'], item['sec'], item['mili']
            ao5 = self.calc_ao(5, min, sec, mili, self.current_session, i)
            self.scores[self.current_session][i]['ao5'] = ao5
            temp[i-index].ao5 = ao5
            i += 1
            j += 1

        i = index
        j = 0
        while i < len(temp) + index and j < 12:
            item = self.scores[self.current_session][i]
            min, sec, mili = item['min'], item['sec'], item['mili']
            ao12 = self.calc_ao(12, min, sec, mili, self.current_session, i)
            self.scores[self.current_session][i]['ao12'] = ao12
            temp[i-index].ao12 = ao12
            i += 1
            j += 1

        for i in temp:
            model.append(i)

        select.set_model(model)
        self.scores_column_view.set_model(select)
        # select.set_selected(len(model)-1)
        self.save_scores()

    def dnf_index(self, index):
        self.scores[self.current_session][index]["time"] = "dnf"
        select = self.scores_column_view.get_model()
        model = select.get_model()

        model[index].time = "dnf"
        l = len(model)
        temp = []
        for i in range(index, l):
            temp.append(Scores(i+1, model[i].time, model[i].ao5, model[i].ao12))

        for i in range(index, l):
            model.remove(index)

        i = index
        j = 0
        while i < len(temp) + index and j < 5:
            item = self.scores[self.current_session][i]
            min, sec, mili = item['min'], item['sec'], item['mili']
            ao5 = self.calc_ao(5, min, sec, mili, self.current_session, i, item["time"])
            self.scores[self.current_session][i]['ao5'] = ao5
            temp[i-index].ao5 = ao5
            i += 1
            j += 1

        i = index
        j = 0
        while i < len(temp) + index and j < 12:
            item = self.scores[self.current_session][i]
            min, sec, mili = item['min'], item['sec'], item['mili']
            ao12 = self.calc_ao(12, min, sec, mili, self.current_session, i, item["time"])
            self.scores[self.current_session][i]['ao12'] = ao12
            temp[i-index].ao12 = ao12
            i += 1
            j += 1

        for i in temp:
            model.append(i)


        select.set_model(model)
        self.scores_column_view.set_model(select)
        self.save_scores()

    def on_clicked(self, widget):
        self.add_session(_(f"Session {len(self.scores.keys())+1}"))

    def on_delete(self, widget): # ??!!
        model = self.dropdown.get_model()
        for i in range(len(model)):
            if model[i].name == self.current_model:
                model.erase(i)
                break
        for i in range(len(model)):
            model[i].name = _(f"Session {i+1}")
        self.dropdown.set_model()

    def add_session(self, session):
        self.scores[session] = []
        model = self.dropdown.get_model()
        model.append(Session(session))
        self.dropdown.set_model(model)
        # self.dropdown.set_selected(len(model)-1)
        self.load_scores(session)

    def on_session_changed(self, widget, arg2):
        model = self.dropdown.get_model()
        self.load_scores(model[self.dropdown.get_selected()].name)

    def load_session_init(self):
        # print(self.button.get_icon_name())
        def f_setup(fact, item):
            label = Gtk.Label(halign=Gtk.Align.START)
            label.set_selectable(False)
            item.set_child(label)

        model = Gio.ListStore()
        fact = Gtk.SignalListItemFactory()
        fact.connect("setup", f_setup)
        def f_bind(fact, item):
            item.get_child().set_label(str(item.get_item().name))
        fact.connect("bind", f_bind)
        self.dropdown.set_factory(fact)
        # print(self.scores.keys())
        for i in self.scores.keys():
            model.append(Session(i))
        if len(model) != 0:
            self.dropdown.set_model(model)
        else:
            model.append(Session("Session 1"))
            self.scores["Session 1"] = []
            self.dropdown.set_model(model)
        self.current_session = model[len(model)-1].name

    def load_scores(self, session):
        if self.current_session == session:
            store = self.scores_column_view.get_model()
            model = store.get_model()
            i: int = len(model)
            while len(model) < len(self.scores[session]):
                model.append(Scores(i+1, self.scores[session][i].get("time"), self.scores[session][i].get("ao5"), self.scores[session][i].get("ao12")))
                i += 1
        else:
            self.current_session = session
            model = Gio.ListStore()
            i: int = 0
            while len(model) < len(self.scores[session]):
                model.append(Scores(i+1, self.scores[session][i].get("time"), self.scores[session][i].get("ao5"), self.scores[session][i].get("ao12")))
                i += 1
        ss = Gtk.SingleSelection()
        ss.set_model(model)
        self.scores_column_view.set_model(ss)
        self.save_scores()

    def add_score(self, time, min, sec, mili, scramble, ao5 = "", ao12 = ""):
        if ao5 == "":
            ao5 = self.calc_ao(5, min, sec, mili, self.current_session, len(self.scores[self.current_session]))
        if ao12 == "":
            ao12 = self.calc_ao(12, min, sec, mili, self.current_session, len(self.scores[self.current_session]))
        self.scores[self.current_session].append({"time": time, "ao5": ao5, "ao12": ao12, "scramble": scramble, "min": min, "sec": sec, "mili": mili})
        self.load_scores(self.current_session)
        self.save_scores()
        model = self.scores_column_view.get_model()
        model.select_item(len(self.scores[self.current_session])-1, 1)

    def calc_ao(self, n, min, sec, mili, session, l, time = ""):
        ao = "-"
        dnf = 0
        t: int = 0
        if l >= n-1:
            for i in range(n-1):
                if self.scores[session][l-i-1].get("time") != "dnf":
                    curr = self.scores[session][l-i-1]
                    t += curr.get("min", 0) * 6000 + curr.get("sec", 0) * 100 + curr.get("mili", 0)
                else:
                    dnf += 1
            if time != "dnf":
                t += min * 6000 + sec * 100 + mili
            else:
                dnf += 1
            t //= (n - dnf)
            amin = t // 6000
            asec = (t % 6000) // 100
            amili = (t - amin * 6000 - asec * 100)
            ao = f"{amin:02d}:{asec:02d}.{amili:02d}"
        if 2 * dnf < n:
            return ao
        else:
            return "dnf"

    def fetch_scores(self):
        with open(scores_file_path, 'a+') as scores_list:
            scores_list.seek(0)
            if os.path.getsize(scores_file_path):
                self.scores = json.load(scores_list)
                self.load_session_init()
                self.load_scores(self.current_session)

    def save_scores(self):
        with open(scores_file_path, 'w') as scores_list:
            json.dump(self.scores, scores_list)
