"""Shared fixtures."""
import json
import logging
from _pytest.fixtures import fixture
from src.cfg.cfg_global import settings
from src.utils import utils
from src.utils.utils import dict_to_obj
from src.web.clients.web_client import BitBucketActivities
from src.api.clients.ManageActivities import ManageActivities

settings_items = [i for i in settings.__dir__() if not i.startswith('_')]


def pytest_addoption(parser) -> None:
    for item in settings_items:
        try:
            value = eval(getattr(settings, item))
        except (SyntaxError, NameError, TypeError, ZeroDivisionError):
            value = getattr(settings, item)
        parser.addoption(F"--{item}", action='store', default=value)


@fixture(scope="session")
def web_client(request):
    """
    start the test's web client.
    :return: test web client.
    """
    logging.info('instantiate the Bitbucket web client')
    web_client = BitBucketActivities(url=settings.url, email=settings.email,
                                     password=request.config.getoption("password"))
    web_client.open_page
    web_client.login
    web_client.go_bitbucket()
    yield web_client
    web_client.tear_down_driver


@fixture(scope="session")
def api_client(request):
    """
    start the test's api client.
    :return: test api client.
    """
    logging.info('instantiate the Bitbucket api client')
    api_client = ManageActivities(refresh_token=request.config.getoption("refresh_token"), client_secret=request.config.getoption("client_secret"))
    yield api_client


@fixture(scope="function")
def clean_web_workspace(web_client):
    web_client.tear_down_resources(settings.new_proj_name, settings.new_repo_name)


@fixture(scope="session")
def tests_data():
    data = dict()
    tmp_settings = settings.__dir__()
    for item in tmp_settings:
        if not item.startswith('_'):
            data[item] = getattr(settings, item)
    return dict_to_obj(data)


@fixture(scope="function")
def cfg_data(test_name):
    cfg_dir, cfg_fn = settings.cfg_tests_dir, F"{test_name}.json"
    return utils.load_data(cfg_dir, cfg_fn)


@fixture(scope="function")
def test_name(request):
    test_name = request.node.name
    return test_name


@fixture(scope="function")
def cfg_data(test_name):
    cfg_dir, cfg_fn = settings.cfg_tests_dir, F"{test_name}.json"
    cfg_data = utils.load_data(cfg_dir, cfg_fn)
    return utils.dict_to_obj(cfg_data)


@fixture(scope="function")
def clean_api(api_client, cfg_data):
    logging.info('++++ in clean_api (tearDown api)')
    api_client.tear_down(cfg_data.proj_key, cfg_data.repo_name)


@fixture(scope="function")
def pre_test_activity(api_client: object, cfg_data: object, clean_api: object):
    """
    creating a project for the repository to be created in
    :param api_client: api client
    :param cfg_data: tests' data
    :param clean_api: tear down before creating the project
    """
    res = api_client.create_proj(cfg_data.proj_name, cfg_data.proj_key)
    assert res.status is True, F"project failed to create, {res.msg}"


@fixture(scope="function")
def logger(request, test_name):
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.DEBUG)
    log_file = f"../../logs/{test_name}.log"
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    yield logger
    logger.handlers = []

