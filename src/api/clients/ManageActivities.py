import json
import logging
from collections import defaultdict

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

    @classmethod
    def resp_handling(cls, func_name, exp_code=None, resp=None, out=None):
        if resp is not None and resp.status_code != exp_code:
            return {"status": False, "msg": F"in {func_name}: {out}, {resp.json()['error']['message']}"}
        else:
            return {"status": True, "msg": F"in {func_name}: success", "result": out}

    def list_repositories(self, proj_name: str, exp_code: int = 200) -> dict:
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        out = []
        url = settings.base_url.format(resource=settings.path_repo)
        resp = requests.request("GET", url, headers=self.general_headers)
        assert resp.status_code == exp_code, (F"in {func_name}; request failed, expected code: {exp_code}, actual: "
                                              F"{resp.status_code}, msg: {resp.text}")
        for val in resp.json().get('values'):
            if val['project']['name'] == proj_name:
                out.append(val['name'])
        return self.resp_handling(func_name, out=out)

    def create_repo(self, repo_name, proj_key, exp_code=200):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        headers = self.update_headers(self.access_token, headers=data['headers'])
        payload = data['payload']
        payload['project']['key'] = payload['project']['key'].format(proj_key=proj_key)
        payload = json.dumps(payload)
        resp = requests.request("POST", url, data=payload, headers=headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=repo_name)

    def create_proj(self, proj_name, proj_key, exp_code=201):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        payload = data['payload']
        payload['key'] = payload['key'].format(proj_key=proj_key)
        payload['name'] = payload['name'].format(proj_name=proj_name)
        payload = json.dumps(payload)
        headers = self.update_headers(self.access_token, headers=data['headers'])
        resp = requests.request("POST", data['url'], data=payload, headers=headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=proj_name)

    def is_proj_exist(self, proj_key):
        pass

    def del_proj(self, proj_key: str, exp_code: int = 204):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(proj_key=proj_key)
        resp = requests.request("GET", url, headers=self.general_headers)
        if resp.status_code == 404:
            return self.resp_handling(func_name=func_name, resp=resp, exp_code=exp_code,
                                      out=F"no project with project key {proj_key}")
        resp = requests.request("DELETE", url, headers=self.general_headers)
        return self.resp_handling(exp_code=exp_code, func_name=func_name, resp=resp, out=F"proj key: {proj_key}")

    def del_repo(self, repo_name, exp_code=204):
        func_name = inspect.currentframe().f_code.co_name
        logging.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        resp = requests.request("GET", url, headers=self.general_headers)
        if resp.status_code == 404:
            return self.resp_handling(func_name=func_name, resp=resp, out=F"no repo with repo name: {repo_name}",
                                      exp_code=exp_code)
        resp = requests.request("DELETE", url, headers=self.general_headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=F"repo name: {repo_name}")

    def tear_down(self, proj_key, repo_name):
        out = defaultdict()
        out['repository'] = self.del_repo(repo_name)
        out['project'] = self.del_proj(proj_key)
        return out


if __name__ == '__main__':
    # inst = ManageActivities('6HY5SHFfeweAsHXvzX')
    inst = ManageActivities(
        access_token='_u_ZaBbFhMp69r4jrjPJpsdFsuh_cnqIp53hKGq3zmvpe1QjAiY_fdiq6MNPN_a9e7VXNUsd7uCAQcc_S5WzMdMUA6pru5NkDkGg97BWbz0VRiJHGq11s9NLdJJgVVnqs7UFk8zqd2r6MInh45gBkO9v9Yy8')

    # proj_name = 'test_proj_01'
    # res = inst.get_proj_key(proj_name)

    proj_name = 'test_proj_02'
    proj_key = 'TES'
    repo_name = 'test_repo_02'
    res = inst.tear_down(proj_key, repo_name)
    print(res)
    # inst.del_repo(repo_name)
    # inst.del_proj(proj_key)
    res = inst.create_proj(proj_name, proj_key)
    print(res)
    res = inst.create_repo(repo_name, proj_key)
    print(res)
    res = inst.list_repositories(proj_name)
    print(res)
