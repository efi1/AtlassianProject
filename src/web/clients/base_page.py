import inspect
import os
import shutil
import logging
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

CHROME_DRIVER_PATH = Path(__file__).parent.parent.joinpath('drivers', 'chromedriver.exe')
TOTAL_SPENT_AMOUNT = 500
IS_INSTALL = os.environ.get('is_install')
IS_RUN_SILENTLY = os.environ.get('is_run_silently')
LOGGER = logging.getLogger()


class BasePage:
    def __init__(self, *args, **kwargs):

        def _convert_arg_to_bool(arg, default=None):
            return arg.lower() in ('yes', 'true', 'y') if arg is not None and len(arg) > 0 else default

        self.options = Options()
        if _convert_arg_to_bool(IS_RUN_SILENTLY):
            self.options.add_argument("headless")
        self.options.add_argument('ignore-certificate-errors')
        window_size = kwargs.get('window_size', 'start-maximized')
        self.options.add_argument(window_size)
        if not Path(CHROME_DRIVER_PATH).exists():
            LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}: no webdriver - creating a new one")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager
                                                           ().install()), options=self.options)
            shutil.copy(self.driver.service.path, CHROME_DRIVER_PATH)
        else:
            service = Service(CHROME_DRIVER_PATH)
            self.driver = webdriver.Chrome(service=service, options=self.options)

    @property
    def tear_down_driver(self):
        self.driver.quit()
