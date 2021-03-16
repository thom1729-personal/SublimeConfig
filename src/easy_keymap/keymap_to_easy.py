from io import StringIO

import re

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq


KEY_ORDER = ['keys', 'command', 'args', 'context']
CONTEXT_KEY_ORDER = ['key', 'operator', 'operand', 'match_all']


def yaml_dumps(value):
    sio = StringIO()
    ruamel.yaml.round_trip_dump(value, sio)
    return re.sub(r'\n\.\.\.\n$', '', sio.getvalue())


def sort_dict(d, keys):
    ret = CommentedMap()
    for key in sorted(d, key=keys.index):
        ret[key] = d[key]
    return ret


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
