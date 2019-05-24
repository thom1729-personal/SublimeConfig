import sublime
import sublime_plugin

from sublime_lib import new_window, new_view

from random import shuffle

__all__ = ['StartMinesCommand', 'MinesListener']

class StartMinesCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        width = 20
        height = 20
        count = 10

        mines = ([True] * count) + ([False] * ((height * width) - count))
        shuffle(mines)

        window = new_window(
            minimap_visible=False,
            sidebar_visible=False,
            tabs_visible=False,
            menu_visible=False,
        )

        view = new_view(
            window,
            scratch=True,
            read_only=True,
            content=(('[ ]'*width + '\n')*height),
            scope='source.mines',
            settings={
                'word_wrap': False,
                'line_numbers': False,
            }
        )

class MinesListener(sublime_plugin.ViewEventListener):
    pass
