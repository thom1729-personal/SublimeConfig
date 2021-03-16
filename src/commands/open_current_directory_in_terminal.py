import sublime
import sublime_plugin

import subprocess
from .path_utils import path_for_view


SCRIPT_PATH = 'Packages/SublimeConfig/src/commands/open_current_directory_in_terminal.applescript'


def osascript(
    *,
    script,
    args=[]
):
    cmd = ['osascript', '-'] + args
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.communicate(input=script)


class OpenCurrentDirectoryInTerminalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        directory, filename = path_for_view(self.view)

        script = sublime.load_binary_resource(SCRIPT_PATH)

        osascript(script=script, args=[directory])
