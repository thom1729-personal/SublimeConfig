import sublime
import sublime_plugin

import ruamel.yaml
from ruamel.yaml.dumper import RoundTripDumper

from pathlib import Path
import json
from textwrap import dedent

from .easy_to_keymap import easy_to_keymap
from .keymap_to_easy import keymap_to_easy


FILE_EXTENSION = '.easy-keymap'


def change_extension(file_name, new_extension):
    path = Path(file_name)
    return str(path.with_name(path.stem + new_extension))


class CompileKeymapCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("Compiling keymap {}…".format(self.view.file_name()))
        text = self.view.substr(sublime.Region(0, self.view.size()))
        value = easy_to_keymap(ruamel.yaml.safe_load(text))

        new_path = change_extension(self.view.file_name(), '.sublime-keymap')
        with open(new_path, 'w+') as outfile:
            json.dump(value, outfile, indent=4, separators=(',', ': '))

        print("Compiled to {}.".format(new_path))


class CreateEasyKeymapCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        text = self.view.substr(sublime.Region(0, self.view.size()))

        value = keymap_to_easy(sublime.decode_value(text))

        new_path = change_extension(self.view.file_name(), FILE_EXTENSION)
        with open(new_path, 'w+') as outfile:
            yaml = ruamel.yaml.YAML()
            yaml.Dumper = RoundTripDumper
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.dump(value, outfile, transform=dedent)


class SaveKeymapListener(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        if view.file_name().endswith(FILE_EXTENSION):
            view.run_command('compile_keymap')
