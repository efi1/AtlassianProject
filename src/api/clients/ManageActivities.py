import json
import logging
import requests
from requests import HTTPError
import inspect
from src.api.clients import handle_token
from importlib.resources import files

from src.cfg.cfg_global import settings


class ManageActivities:
    def __init__(self, refresh_token=None, access_token=None):
        self.access_token = access_token if access_token else handle_token.HandleToken(refresh_token).get_oauth_token()
        self.general_headers = self.get_general_headers()

    @classmethod
    def update_headers(cls, access_token, headers):
        return {key: headers[key].format(access_token=access_token) for key in headers}

    def get_general_headers(self):
        data = self.get_api_data(settings.api_default_data_fn)
        return self.update_headers(self.access_token, headers=data.get('headers'))

    @classmethod
    def get_api_data(cls, fn):
        f_path = files(settings.api_data_dir).joinpath(F"{fn}.json")
        with open(f_path, 'r') as fn:
            return json.load(fn)

    def get_proj_key(self, proj_name):
        url = settings.base_url.format(resource=settings.path_repo)
        resp = requests.request("GET", url, headers=self.general_headers)
        for val in resp.json().get('values'):
            if val['project']['name'] == proj_name:
                return val['project']['key']

    def list_repositories(self, proj_name):
        out = []
        url = settings.base_url.format(resource=settings.path_repo)
        resp = requests.request("GET", url, headers=self.general_headers)
        assert resp.status_code == 200, F"request failed, {resp.text}"
        for val in resp.json().get('values'):
            if val['project']['name'] == proj_name:
                out.append(val['name'])
        return out

    def list_repos(self, proj_name):
        proj_key = self.get_proj_key(proj_name)
        url = settings.repo_by_key_url.format(proj_key=proj_key)
        resp = requests.request("GET", url, headers=self.general_headers)
        return [val['name'] for val in resp.json().get('values')]

    def create_repo(self, repo_name, proj_key):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        payload = data['payload']
        payload['project']['key'] = payload['project']['key'].format(proj_key=proj_key)
        payload = json.dumps(payload)
        resp = requests.request("POST", url, data=payload, headers=self.general_headers)
        assert resp.status_code == 200, F"request failed, expected code: 201, actual: {resp.status_code}, msg: {resp.text}"

    def create_proj(self, proj_name, proj_key):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        payload = data['payload']
        payload['key'] = payload['key'].format(proj_key=proj_key)
        payload['name'] = payload['name'].format(proj_name=proj_name)
        payload = json.dumps(payload)
        headers = self.update_headers(self.access_token, headers=data['headers'])
        resp = requests.request("POST", data['url'], data=payload, headers=headers)
        assert resp.status_code == 201, F"request failed, expected code: 201, actual: {resp.status_code}, msg: {resp.text}"

    def del_proj(self, proj_key):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(proj_key=proj_key)
        resp = requests.request("DELETE", url, headers=self.general_headers)
        assert resp.status_code == 204, F"request failed, expected code: 201, actual: {resp.status_code}, msg: {resp.text}"

    def del_repo(self, repo_name):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        resp = requests.request("DELETE", url, headers=self.general_headers)
        assert resp.status_code == 204, F"request failed, expected code: 201, actual: {resp.status_code}, msg: {resp.text}"


if __name__ == '__main__':
    inst = ManageActivities('6HY5SHFfeweAsHXvzX')
    inst = ManageActivities(
        access_token='ry8wWIwdTWo8-oBd5raINm8Fpabpe9NkzaX9qqh0mbn4yJDJ9Nu9g3s8fzeyu8Q5MJ34xq1tF8AM9GMxbLAzrFbzuZB9OLyQtuXJDNx96tfJCn0jAidaI08-6UIu4xmk8j1Z_YtIB2S1w-zFtVKhrdTh8Uc=')

    # proj_name = 'test_proj_01'
    # res = inst.get_proj_key(proj_name)

    proj_name = 'test_proj_02'
    proj_key = 'TES'
    repo_name = 'test_repo_02'

    inst.create_proj(proj_name, proj_key)
    inst.create_repo(repo_name, proj_key)
    res = inst.list_repositories(proj_name)
    print(res)
    res = inst.list_repos(proj_name)
    print(res)
    inst.del_repo(repo_name)
    inst.del_proj(proj_key)



