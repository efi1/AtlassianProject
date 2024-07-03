import json
import requests
from src.cfg.cfg_global import settings
from importlib.resources import files


class HandleToken:
    def __init__(self, refresh_token=None, client_secret=None):
        self.refresh_token = refresh_token
        self.client_secret = client_secret
        self.access_token = None
        self.data_path = files(settings.cfg_global_dir).joinpath(settings.data_access)

    def get_refreshed_token(self, **kwargs):
        auth = (kwargs['client_id'], self.client_secret)
        params = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        url = kwargs['auth_domain']
        ret = requests.post(url, auth=auth, data=params)
        return ret

    def _load_access_data(self):
        file_path = self.data_path
        with open(file_path, 'r') as fn:
            return json.load(fn)

    def get_oauth_token(self):
        data_access = self._load_access_data()
        new_token = self.get_refreshed_token(**data_access).json().get('access_token')

        return new_token

