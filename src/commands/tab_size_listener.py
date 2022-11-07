import sublime
import sublime_plugin

from .settings_listener import ViewSettingsListener, on_setting_changed


__all__ = ('ResizeExistingTabsCommand', 'TabSizeListener')


class ResizeExistingTabsCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, *, old_size: int, new_size: int) -> None:  # type: ignore[override]
        settings = self.view.settings()

        lines = self.view.lines(sublime.Region(0, self.view.size()))

        auto_indent = settings.get('auto_indent')
        settings.set('auto_indent', False)

        for line in reversed(lines):
            text = self.view.substr(line)
            leading_spaces = len(text) - len(text.lstrip(' '))
            indent_level = leading_spaces // old_size
            new_indentation = ' ' * new_size * indent_level
            self.view.replace(
                edit,
                sublime.Region(line.begin(), line.begin() + old_size * indent_level),
                new_indentation
            )

        settings.set('auto_indent', auto_indent)


class TabSizeListener(ViewSettingsListener):
    _loaded = False

    @classmethod
    def is_applicable(cls, settings: sublime.Settings) -> bool:
        return settings.get('translate_tabs_to_spaces', False)

    @classmethod
    def applies_to_primary_view_only(cls) -> bool:
        return True

    def on_load(self) -> None:
        self._loaded = True

    @on_setting_changed('tab_size')
    def tab_size_changed(self, new_value: object, old_value: object) -> None:
        if not self._loaded: return
        self.view.run_command('resize_existing_tabs', {
            'new_size': new_value,
            'old_size': old_value,
        })
