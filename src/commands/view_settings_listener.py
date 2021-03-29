from abc import ABCMeta, abstractmethod
import sublime
import sublime_plugin

from collections import namedtuple
import weakref


__all__ = ('ViewSettingsListener', 'on_setting_changed')


OnChangedOptions = namedtuple('OnChangedOptions', ('selector'))
OPTIONS_ATTRIBUTE = '_OnChangedOptions'


def on_setting_changed(selector):
    if callable(selector):
        selector_function = selector
    else:
        selector_function = lambda settings: settings.get(selector)

    def decorator(function):
        setattr(function, OPTIONS_ATTRIBUTE, OnChangedOptions(selector_function))
        return function

    return decorator


class BaseSettingsListener(metaclass=ABCMeta):
    @abstractmethod
    def _settings(self) -> sublime.Settings:
        ...

    def _handlers(self):
        for name in dir(self):
            value = getattr(self, name)
            options = getattr(value, OPTIONS_ATTRIBUTE, None)

            if not name.startswith('_') and options is not None:
                yield name, value, options

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        weak_self = weakref.ref(self)

        def on_change():
            this = weak_self()
            if this is not None:
                this._on_settings_changed()

        self._settings().add_on_change(str(id(self)), on_change)

        self._last_known_values = {
            name: options.selector(self._settings())
            for name, _, options in self._handlers()
        }

    def __del__(self):
        self._settings().clear_on_change(str(id(self)))

    def _on_settings_changed(self):
        for name, handler, options in self._handlers():
            previous_value = self._last_known_values[name]
            current_value = options.selector(self._settings())

            if current_value != previous_value:
                self._last_known_values[name] = current_value
                handler(current_value, previous_value)


class ViewSettingsListener(BaseSettingsListener, sublime_plugin.ViewEventListener):
    def _settings(self):
        return self.view.settings()
