import sublime
import sublime_plugin

class StatusMessageCommand(sublime_plugin.WindowCommand):
    def run(self, message):
        self.window.status_message(message)
