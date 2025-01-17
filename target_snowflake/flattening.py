import collections
import inflection
import itertools
import json
import re


def flatten_key(k, parent_key, sep):
    """

    Params:
        k:
        parent_key:
        sep:

    Returns:
    """
    full_key = parent_key + [k]
    inflected_key = full_key.copy()
    reducer_index = 0
    while len(sep.join(inflected_key)) >= 255 and reducer_index < len(inflected_key):
        reduced_key = re.sub(r'[a-z]', '', inflection.camelize(inflected_key[reducer_index]))
        inflected_key[reducer_index] = \
            (reduced_key if len(reduced_key) > 1 else inflected_key[reducer_index][0:3]).lower()
        reducer_index += 1

    return sep.join(inflected_key)


# pylint: disable=invalid-name
def flatten_schema(d, parent_key=None, sep='__', level=0, max_level=0):
    """

    Params:
        k:
        parent_key:
        sep:

    Returns:
    """
    if parent_key is None:
        parent_key = []

    items = []
    if 'properties' not in d:
        return {}

    for k, v in d['properties'].items():
        new_key = flatten_key(k, parent_key, sep)
        if 'type' in v.keys():
            if 'object' in v['type'] and 'properties' in v and level < max_level:
                items.extend(flatten_schema(v, parent_key + [k], sep=sep, level=level + 1, max_level=max_level).items())
            else:
                items.append((new_key, v))
        else:
            if len(v.values()) > 0:
                if list(v.values())[0][0]['type'] == 'string':
                    list(v.values())[0][0]['type'] = ['null', 'string']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == 'array':
                    list(v.values())[0][0]['type'] = ['null', 'array']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == 'object':
                    list(v.values())[0][0]['type'] = ['null', 'object']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == 'integer':
                    list(v.values())[0][0]['type'] = ['null', 'integer']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == 'number':
                    list(v.values())[0][0]['type'] = ['null', 'number']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == 'boolean':
                    list(v.values())[0][0]['type'] = ['null', 'boolean']
                    items.append((new_key, list(v.values())[0][0]))
                elif list(v.values())[0][0]['type'] == ['null', 'string']:
                    items.append((new_key, list(v.values())[0][0]))
                else:
                    raise ValueError(f"Unknown schema property type for key '{k}': {json.dumps(v)}")

    key_func = lambda item: item[0]
    sorted_items = sorted(items, key=key_func)
    for k, g in itertools.groupby(sorted_items, key=key_func):
        if len(list(g)) > 1:
            raise ValueError(f'Duplicate column name produced in schema: {k}')

    return dict(sorted_items)


def _should_json_dump_value(key, value, schema=None):
    """

    Params:
        k:
        parent_key:
        sep:

    Returns:
    """
    if isinstance(value, (dict, list)):
        return True

    if schema and key in schema and 'type' in schema[key] and set(
            schema[key]['type']) == {'null', 'object', 'array'}:
        return True

    return False


# pylint: disable-msg=invalid-name
def flatten_record(d, schema=None, parent_key=None, sep='__', level=0, max_level=0):
    """

    Params:
        k:
        parent_key:
        sep:

    Returns:
    """
    if parent_key is None:
        parent_key = []

    items = []
    for k, v in d.items():
        new_key = flatten_key(k, parent_key, sep)
        if isinstance(v, collections.abc.MutableMapping) and level < max_level:
            items.extend(flatten_record(v, schema, parent_key + [k], sep=sep, level=level + 1,
                                        max_level=max_level).items())
        else:
            items.append((new_key, json.dumps(v) if _should_json_dump_value(k, v, schema) else v))

    return dict(items)
