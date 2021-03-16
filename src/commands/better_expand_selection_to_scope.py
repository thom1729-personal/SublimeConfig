import sublime_plugin

import re


class BetterExpandSelectionToScopeCommand(sublime_plugin.TextCommand):
    def split_scope(self, pos):
        return re.findall(
            r'(?:^|\s+|\.)[^\s.]+',
            self.view.scope_name(pos)
        )

    def find_by_selector_containing(self, selector, point):
        return next(
            region
            for region in self.view.find_by_selector(selector)
            if region.contains(point)
        )

    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            expanded = self.get_expanded(region)
            if expanded:
                selection.add(expanded)

    def get_expanded(self, inner):
        target = self.split_scope(inner.begin())

        while len(target):
            outer = self.find_by_selector_containing(''.join(target), inner.begin())
            if outer.contains(inner) and not inner.contains(outer):
                print(''.join(target))
                return outer
            else:
                target.pop()
