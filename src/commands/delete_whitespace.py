import sublime_plugin
from sublime import Region


class DeleteWhitespaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction=None):
        for caret in self.view.sel():

            if direction in ["right", "both"]:
                pos = caret.end()
                while self.view.substr(pos).isspace():
                    pos += 1
                self.view.erase(edit, Region(caret.end(), pos))

            if direction in ["left", "both"]:
                pos = caret.begin()
                while self.view.substr(pos - 1).isspace():
                    pos -= 1
                self.view.erase(edit, Region(caret.begin(), pos))
