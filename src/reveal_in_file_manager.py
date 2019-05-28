import sublime
import sublime_plugin

from os.path import split

class RevealInFileManagerCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = self.view.window()
        current_file = self.view.file_name()
        if current_file is not None:
            dirname, filename = split(current_file)
            args = {
                'dir': dirname,
                'file': filename,
            }
        elif window.folders():
            args = {
                'dir': window.folders()[0],
            }
        else:
            raise ValueError("No file name or window folders.")

        window.run_command('open_dir', args)
