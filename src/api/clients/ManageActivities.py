import json
import logging
import requests
from atlassian.bitbucket import Cloud
from atlassian import Bitbucket
from requests import HTTPError

from src.api.get_access_token import Auth0Client


# token is a dictionary and must at least contain "access_token"
# and "token_type".

class ManageBitbucket:
    def __init__(self, token, *rgs, **kwargs):
        self.token = ''





