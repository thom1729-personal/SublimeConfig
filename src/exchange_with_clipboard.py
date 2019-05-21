import sublime, sublime_plugin

class ExchangeWithClipboardCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        old = sublime.get_clipboard()

        self.view.run_command('copy')
        new = sublime.get_clipboard()

        sublime.set_clipboard(old)
        self.view.run_command('paste')

        sublime.set_clipboard(new)
