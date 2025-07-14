import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk
from .window import CubeTimerWindow
from .utils import scores_file_path

class CubeTimerApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.vallabhvidy.CubeTimer',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/io/github/vallabhvidy/CubeTimer/')

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('view_scores', self.on_view_scores)
        # self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's min window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CubeTimerWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog.new_from_appdata("io/github/vallabhvidy/CubeTimer/metainfo.xml", "0.1.3")
        about.set_developers(["Vallabh Vidyasagar https://github.com/vallabhvidy"])
        # Translators: Replace "translator-credits" with your names, one name per line
        about.set_translator_credits(_("translator-credits"))
        about.set_copyright("© 2025 Vallabh Vidyasagar")
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def on_view_scores(self, widget, _):
        file = Gio.File.new_for_path(str(scores_file_path))
        file_launcher = Gtk.FileLauncher(
            always_ask=True,
            file=file,
        )

        file_launcher.open_containing_folder()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action("app.{name}".format(name=name), shortcuts)


def main(version):
    """The application's entry point."""
    app = CubeTimerApplication()
    return app.run(sys.argv)
