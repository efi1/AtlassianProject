import json
import requests
from pathlib import Path
from from_root import from_root, from_here


# data_path = '../../cfg/cfg_global/data_access.json'


class HandleToken:
    def __init__(self, refresh_token):
        self.refresh_token = refresh_token

    def get_refreshed_token(cls, **kwargs):
        auth = (kwargs['client_id'], kwargs['client_secret'])
        params = {"grant_type": "refresh_token", "refresh_token": kwargs['refresh_token']}
        url = kwargs['auth_domain']
        ret = requests.post(url, auth=auth, data=params)
        return ret

    def load_access_data(self, data_access_fn):
        # data_path = from_root()
        data_path = Path(from_root()).joinpath('cfg').joinpath()
        with open(data_path, 'r') as fn:
            return json.load(fn)

    def update_data(self, new_access_token, data):
        data['access_token'] = new_access_token
        with open('data_access.json', 'w') as fn:
            fn.write(json.dumps(data))


if __name__ == '__main__':
    inst = HandleToken('6HY5SHFfeweAsHXvzX')
    data_access = inst.load_access_data('data_access.json')
    new_token = inst.get_refreshed_token(**data_access).json()
    inst.update_data(new_token.get('access_token'), data_access)

