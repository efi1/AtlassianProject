import json
import os
import webbrowser
from pathlib import Path


class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)


def dict_to_obj(d):
    return json.loads(json.dumps(d), object_pairs_hook=obj)
