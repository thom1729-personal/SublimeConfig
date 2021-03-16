import sublime_plugin


class IncrementCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selections = self.view.sel()

        start = self.view.substr(selections[0])
        i = int(start)
        w = len(start)

        c = ' ' if start[0] == ' ' else '0'

        print(start, i, w)

        for region in selections:
            self.view.replace(edit, region, str(i).rjust(w, c))
            i += 1
