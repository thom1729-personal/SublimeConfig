import sublime
import sublime_plugin

import ruamel.yaml
from ruamel.yaml.dumper import RoundTripDumper
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from pathlib import Path
from io import StringIO
import json
import re
from textwrap import dedent


FILE_EXTENSION = '.easy-keymap'
KEY_ORDER = ['keys', 'command', 'args', 'context']
CONTEXT_KEY_ORDER = ['key', 'operator', 'operand', 'match_all']

CONDITION_EXPR = re.compile(r"""
    (?:(?P<quantifier>all)\s+)?
    (?P<key>\w+)
    \s+(?P<operator>\w+)
    \s+(?P<operand>
        '(?:[^']|'')*'
        |"(?:[^"\\]|\\.)*"
        |\S+
    )
""", re.X)


def yaml_dumps(value):
    sio = StringIO()
    ruamel.yaml.round_trip_dump(value, sio)
    return re.sub(r'\n\.\.\.\n$', '', sio.getvalue())


def change_extension(file_name, new_extension):
    path = Path(file_name)
    return str(path.with_name(path.stem + new_extension))


def sort_dict(d, keys):
    ret = CommentedMap()
    for key in sorted(d, key=keys.index):
        ret[key] = d[key]
    return ret


def easy_to_keymap(easy):
    def get_condition(condition):
        if isinstance(condition, str):
            match = CONDITION_EXPR.match(condition)

            ret = {
                'key': match.group('key'),
                'operator': match.group('operator'),
                'operand': ruamel.yaml.load(match.group('operand')),
            }

            if match.group('quantifier'):
                ret['match_all'] = True

            return ret
        else:
            return condition

    def get_command(command):
        if isinstance(command, dict):
            commands = list(command.items())

            if len(commands) == 1:
                name, args = commands[0]
                return ( name, args )
        else:
            return ( command, None )

    def get_entry(entry):
        ret = entry.copy()

        if isinstance(ret['keys'], str):
            ret['keys'] = [ ret['keys'] ]

        if isinstance(ret['command'], list):
            ret['args'] = {
                'commands': [
                    [ command, args ]
                    for command, args in map(get_command, ret['command'])
                ]
            }
            ret['command'] = 'chain'
        else:
            command, args = get_command(ret['command'])
            ret['command'] = command
            if args is not None:
                ret['args'] = args

        if 'context' in ret:
            ret['context'] = list(map(get_condition, ret['context']))

        return ret

    return list(map(get_entry, easy))


def keymap_to_easy(keymap):
    def get_condition(condition):
        quantifier_string = 'all ' if condition.get('match_all', False) else ''
        return "{quantifier}{key} {operator} {operand}".format(
            quantifier=quantifier_string,
            key=condition['key'],
            operator=condition['operator'],
            operand=yaml_dumps(condition['operand']),
        )

    def get_entry(entry):
        ret = {}

        if len(entry['keys']) == 1:
            ret['keys'] = entry['keys'][0]
        else:
            ret['keys'] = entry['keys']

        if 'args' in entry:
            if entry['command'] == 'chain':
                ret['command'] = [
                    cmd[0] if len(cmd) == 1
                    else {
                        cmd[0]: cmd[1]
                    }
                    for cmd in entry['args']['commands']
                ]
            else:
                ret['command'] = {
                    entry['command']: entry['args']
                }
        else:
            ret['command'] = entry['command']

        if 'context' in entry:
            ret['context'] = [
                get_condition(condition)
                for condition in entry['context']
            ]

        return sort_dict(ret, KEY_ORDER)

    ret = CommentedSeq()
    for i, entry in enumerate(keymap):
        ret.append(get_entry(entry))
        if i > 0:
            ret.yaml_set_comment_before_after_key(i, before='\n\n')

    return ret


class CompileKeymapCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        text = self.view.substr(sublime.Region(0, self.view.size()))
        value = easy_to_keymap(ruamel.yaml.safe_load(text))

        new_path = change_extension(self.view.file_name(), '.sublime-keymap')
        with open(new_path, 'w+') as outfile:
            json.dump(value, outfile, indent=4)


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
