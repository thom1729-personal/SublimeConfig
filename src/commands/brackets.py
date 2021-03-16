import sublime, sublime_plugin
from sublime import Region

from sublime_lib.flags import QueryContextOperator


PAIRS = { '()', '{}', '[]' }


def query_context_decorator(key):
    desired_key = key
    def decorator(function):
        def on_query_context(self, key, operator, operand, match_all=False):
            if (key != desired_key): return None

            quantifier = all if match_all else any
            predicate = QueryContextOperator(operator)

            return quantifier(
                predicate.apply(function(self, region), operand)
                for region in self.view.sel()
            )

        return on_query_context

    return decorator


class BracketsContext(sublime_plugin.ViewEventListener):
    @query_context_decorator('in_brackets')
    def on_query_context(self, region):
        before = self.view.substr(Region(0, region.begin())).rstrip()
        after  = self.view.substr(Region(region.end(), self.view.size())).lstrip()

        return (
            len(before) > 0  and len(after) > 0
            and (before[-1] + after[0]) in PAIRS
        )
