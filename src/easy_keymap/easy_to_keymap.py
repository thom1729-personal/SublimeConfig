import ruamel.yaml
from ruamel.yaml.dumper import RoundTripDumper
from ruamel.yaml.comments import CommentedMap, CommentedSeq

import re


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


def easy_to_keymap(easy):
    def get_condition(condition):
        if isinstance(condition, str):
            match = CONDITION_EXPR.match(condition)

            ret = {
                'key': match.group('key'),
                'operator': match.group('operator'),
                'operand': ruamel.yaml.safe_load(match.group('operand')),
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
