import sublime
import sublime_plugin
import re

from sublime_lib import show_selection_panel


TRANSFORMS = {
    "hyphen"    : lambda words: '-'.join(words),
    "underscore": lambda words: '_'.join(words),
    "shouty"    : lambda words: '_'.join([ word.upper() for word in words ]),

    "pascal": lambda words: ''.join([ word.capitalize() for word in words ]),
    "camel" : lambda words: ''.join(words[:1] + [ word.capitalize() for word in words[1:] ]),
}


def split_words(s):
    indices = list(
        [ match.start(), match.end() ]
        for match in re.finditer(r'\s+|_|-|(?<=[a-z])(?=[A-Z])', s)
    )

    starts = [0] + [ end for start, end in indices ]
    ends   = [ start for start, end in indices ] + [ len(s) ]

    for start, end in zip(starts, ends):
        yield s[start:end].lower()


class RecaseSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, case=None):
        for region in self.view.sel():
            original = self.view.substr(region)
            words = list(split_words(original))

            self.view.replace(edit, region, TRANSFORMS[case](words))


class TransformWordsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        first_selection = self.view.substr(self.view.sel()[0])
        items = [
            [name.capitalize(), function(list(split_words(first_selection)))]
            for name, function in TRANSFORMS.items()
        ]
        print(items)

        def replace(item):
            name, function = item
            self.view.run_command('recase_selection', { 'case': name })

        show_selection_panel(self.view.window(), items, on_select=replace)
