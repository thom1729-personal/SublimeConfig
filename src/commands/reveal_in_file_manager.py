import sublime
import sublime_plugin

from .path_utils import path_for_view

class RevealInFileManagerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        directory, filename = path_for_view(self.view)

        self.view.window().run_command('open_dir', {
            'dir': directory,
            'file': filename,
        })
