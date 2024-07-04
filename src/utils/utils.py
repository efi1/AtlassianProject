import json
from importlib.resources import files


class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)


def dict_to_obj(d):
    return json.loads(json.dumps(d), object_pairs_hook=obj)


def load_data(json_dir: str = None, json_file: str = None, json_path=None) -> dict:
    """
    loading content from a json file
        - you may either give a full path in a single argument or give both the folder
          and the file name in a separate arguments
    :param json_dir: folder
    :param json_file: file name
    :param json_path: full file path
    :return: dictionary of the file content
    """
    if all([json_dir, json_file]):
        json_path = files(json_dir).joinpath(json_file)
    elif not json_path:
        raise ValueError('missing argument/s')
    try:
        with open(json_path, '+r') as file:
            data = json.loads(file.read())
    except FileExistsError:
        raise ValueError("Path not exists")
    return data
