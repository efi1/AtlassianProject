"""Shared fixtures."""
import logging
from _pytest.fixtures import fixture
from src.cfg.cfg_global import settings
from src.utils.utils import dict_to_obj
from src.web.clients.web_client import BitBucketActivities


@fixture(scope="session")
def web_client(request):
    """
    start the test's client.
    :return: test web client.
    """
    logging.info('initiate the Bitbucket web client')
    web_client = BitBucketActivities(url=settings.url, email=settings.email, password=settings.password)
    web_client.open_page
    web_client.login
    web_client.go_bitbucket()
    yield web_client
    web_client.tear_down_driver


@fixture(scope="function")
def clean_workspace(web_client):
    web_client.tear_down_resources(settings.new_proj_name, settings.new_repo_name)


@fixture(scope="session")
def tests_data():
    data = dict()
    tmp_settings = settings.__dir__()
    for item in tmp_settings:
        if not item.startswith('_'):
            data[item] = getattr(settings, item)
    return dict_to_obj(data)
