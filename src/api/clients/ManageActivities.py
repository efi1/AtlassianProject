import json
from collections import defaultdict
import requests
import inspect
from src.api.clients import handle_token
from importlib.resources import files
from src.utils.utils import dict_to_obj
from src.cfg.cfg_global import settings
import logging

LOGGER = logging.getLogger()


class ManageActivities:
    def __init__(self, refresh_token=None, client_secret=None, access_token=None):
        self.access_token = access_token if access_token else handle_token.HandleToken(refresh_token, client_secret).get_oauth_token()
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
    def resp_handling(cls, func_name, exp_code=None, resp=None, out=None) -> object:
        """
        parsing the result of the other function in a readable message
        :param func_name: the caller function
        :param exp_code: the expected code status of the caller
        :param resp: the caller response.
        :param out: caller output (e.g. values like repo list)
        :return: an object with the response message, also a status - True for success, False for failed.
        """
        if resp is not None and resp.status_code != exp_code:
            LOGGER.info(F"in {func_name}: {out}, {resp.json()['error']['message']}")
            return dict_to_obj({"status": False, "msg": F"in {func_name}: {out}, {resp.json()['error']['message']}"})
        else:
            LOGGER.info(F"in {func_name}: success, result: {out}")
            return dict_to_obj({"status": True, "msg": F"in {func_name}: success", "result": out})

    def list_repositories(self, proj_name: str, exp_code: int = 200) -> dict:
        func_name = inspect.currentframe().f_code.co_name
        LOGGER.info(F"++++ in {func_name}")
        out = []
        url = settings.base_url
        resp = requests.request("GET", url, headers=self.general_headers)
        assert resp.status_code == exp_code, (F"in {func_name}; request failed, expected code: {exp_code}, actual: "
                                              F"{resp.status_code}, msg: {resp.text}")
        for val in resp.json().get('values'):
            if val['project']['name'] == proj_name:
                out.append(val['name'])
        return self.resp_handling(func_name, out=out)

    def create_repo(self, repo_name, proj_key, exp_code=200) -> object:
        """
        create a new repo in a specified Bitbucket project.
        :param exp_code: the expected status_code of the REST request.
        :return: an object with the response message, also a status - True for success, False for failed.
        """
        func_name = inspect.currentframe().f_code.co_name
        LOGGER.info(F"++++ in {func_name}, creating {repo_name}...")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        headers = self.update_headers(self.access_token, headers=data['headers'])
        payload = data['payload']
        payload['project']['key'] = payload['project']['key'].format(proj_key=proj_key)
        payload = json.dumps(payload)
        resp = requests.request("POST", url, data=payload, headers=headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=repo_name)

    def create_proj(self, proj_name, proj_key, exp_code=201) -> object:
        """
        create a new project within a specified Bitbucket workspace.
        :param proj_name: project name
        :param proj_key: the project's key
        :param exp_code: the expected status_code of the REST request.
        :return: an object with the response message, also a status - True for success, False for failed.
        """
        func_name = inspect.currentframe().f_code.co_name
        LOGGER.info(F"++++ in {func_name}, creating {proj_name}...")
        data = self.get_api_data(func_name)
        payload = data['payload']
        payload['key'] = payload['key'].format(proj_key=proj_key)
        payload['name'] = payload['name'].format(proj_name=proj_name)
        payload = json.dumps(payload)
        headers = self.update_headers(self.access_token, headers=data['headers'])
        resp = requests.request("POST", data['url'], data=payload, headers=headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=proj_name)

    def del_proj(self, proj_key: str, exp_code: int = 204) -> object:
        """
        delete a project from a specified Bitbucket workspace.
        :param proj_key: proj_key: the project's key
        :param exp_code: the expected status_code of the REST request.
        :return:  an object with the response message, also a status - True for success, False for failed.
        """
        func_name = inspect.currentframe().f_code.co_name
        LOGGER.info(F"++++ in {func_name}, deleting project, proj. key: {proj_key}")
        data = self.get_api_data(func_name)
        url = data['url'].format(proj_key=proj_key)
        resp = requests.request("GET", url, headers=self.general_headers)
        if resp.status_code == 404:
            return self.resp_handling(func_name=func_name, resp=resp, exp_code=exp_code,
                                      out=F"no project with project key {proj_key}")
        resp = requests.request("DELETE", url, headers=self.general_headers)
        return self.resp_handling(exp_code=exp_code, func_name=func_name, resp=resp, out=F"proj key: {proj_key}")

    def del_repo(self, repo_name, exp_code=204) -> object:
        """
        delete a repo from a specified Bitbucket project.
        :param repo_name: repo name.
        :param exp_code: the expected status_code of the REST request.
        :return: exp_code: an object with the response message, also a status - True for success, False for failed.
        """
        func_name = inspect.currentframe().f_code.co_name
        LOGGER.info(F"++++ in {func_name}")
        data = self.get_api_data(func_name)
        url = data['url'].format(repo_name=repo_name)
        resp = requests.request("GET", url, headers=self.general_headers)
        if resp.status_code == 404:
            return self.resp_handling(func_name=func_name, resp=resp, out=F"no repo with repo name: {repo_name}",
                                      exp_code=exp_code)
        resp = requests.request("DELETE", url, headers=self.general_headers)
        return self.resp_handling(resp=resp, exp_code=exp_code, func_name=func_name, out=F"repo name: {repo_name}")

    def tear_down(self, proj_key, repo_name) -> dict:
        """
        cll both delete repo and delete project
        :param proj_key: project's key.
        :param repo_name: repo name.
        :return: a dict with both output
        """
        out = defaultdict()
        out['repository'] = self.del_repo(repo_name)
        out['project'] = self.del_proj(proj_key)
        return out
