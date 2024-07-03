import json
import requests
from src.cfg.cfg_global import settings
from importlib.resources import files


class HandleToken:
    def __init__(self, refresh_token=None):
        self.refresh_token = refresh_token
        self.access_token = None
        self.data_path = files(settings.cfg_global_dir).joinpath(settings.data_access)

    @classmethod
    def _get_refreshed_token(cls, **kwargs):
        auth = (kwargs['client_id'], kwargs['client_secret'])
        params = {"grant_type": "refresh_token", "refresh_token": kwargs['refresh_token']}
        url = kwargs['auth_domain']
        ret = requests.post(url, auth=auth, data=params)
        return ret

    def _load_access_data(self):
        file_path = self.data_path
        with open(file_path, 'r') as fn:
            return json.load(fn)

    def _update_data(self, new_access_token, data):
        data['access_token'] = new_access_token
        with open(self.data_path, 'w') as fn:
            fn.write(json.dumps(data))

    def get_oauth_token(self):
        data_access = self._load_access_data()
        if self.refresh_token:
            data_access['refresh_token'] = self.refresh_token
        elif not data_access['refresh_token']:
            return
        new_token = self._get_refreshed_token(**data_access).json().get('access_token')
        self._update_data(new_token, data_access)
        return new_token


if __name__ == '__main__':
    inst = HandleToken()
    print(inst.access_token)
    # inst = HandleToken('6HY5SHFfeweAsHXvzX')
    # get_oauth_token = inst._get_oauth_token
    # print(get_oauth_token)
