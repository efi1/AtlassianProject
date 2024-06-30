import time
import logging
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from src.web.clients.locator import Locator

LOGGER = logging.getLogger()

EXPECTED_CONDITIONS_ELEMENT = \
    {
        'visibility': 'visibility_of_element_located',
        'presence': 'presence_of_element_located',
        'text': 'text_to_be_present_in_element',
        'clickable': 'element_to_be_clickable'
    }


class BaseElements(object):

    def __init__(self, driver):
        self.element = None
        self.driver = driver

    def find(self, by, value, element=None, expected_condition=None, timeout=5):
        locator = BaseElements.get_locator(by, value)
        if expected_condition:
            element = WebDriverWait(element if element else self.driver, timeout).until(
                getattr(EC, EXPECTED_CONDITIONS_ELEMENT.get(expected_condition))(locator))
        else:
            element = getattr(element if element else self.driver, 'find_element')(locator.by, locator.value)
        return element

    @staticmethod
    def retry_removed_element(func):
        def wrapper(self, *args, **kwargs):
            timeout = kwargs.get('wrapper_timeout', 5)
            start_time = time.time()
            while time.time() - start_time <= timeout:
                self.driver.refresh()
                try:
                    return func(self, *args, **kwargs)
                except TimeoutException as e:
                    LOGGER.info('element removed')
                    return True
            return False

        return wrapper

    @retry_removed_element
    def is_elem_removed(self, by, value, expected_condition=None, timeout=2, retry_timeout=10):
        self.find(by, value, expected_condition='clickable', timeout=timeout)

    @staticmethod
    def retry_not_clickable(func):
        def wrapper(*args, **kwargs):
            timeout = kwargs.get('retry_timeout', 30)
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    return func(*args, **kwargs)
                except (EC.StaleElementReferenceException, ElementClickInterceptedException) as e:
                    LOGGER.info(F"Error occurred:\n{e.msg}\nRetrying...")
            raise Exception("***   element is not clickable")

        return wrapper

    # Example usage
    @retry_not_clickable
    def click_element(self, by, value, expected_condition='clickable', timeout=10, retry_timeout=30):
        self.find(by, value, expected_condition=expected_condition, timeout=timeout).click()

    def select_dropdown(self, cur, desired):
        cur_readme_selection = self.find('xpath', F"//*[text()='{cur}']", expected_condition='clickable')
        cur_readme_selection.click()
        option = self.find('xpath', F"//*[text()='{desired}']", expected_condition='clickable')
        self.driver.execute_script("arguments[0].scrollIntoView();", option)
        option.click()

    @staticmethod
    def get_locator(by, value):
        return Locator(by, value)

    @property
    def go_back(self):
        self.driver.back()

    def supress_time_exception(self, locator, value, expected_condition='presence', timeout=2) -> [None | object]:
        """
        supress find element response when time exception raised
        :param locator: locator
        :param value: search value
        :param expected_condition:
        :return: response ot None if exception occurred
        """
        try:
            res = self.find(locator, value, expected_condition=expected_condition, timeout=timeout)
        except TimeoutException:
            return None
        return res
