import time
import logging
from functools import wraps

from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from src.web.clients.locator import Locator

LOGGER = logging.getLogger()

EXPECTED_CONDITIONS_ELEMENT = {
    'visibility': 'visibility_of_element_located',
    'presence': 'presence_of_element_located',
    'text': 'text_to_be_present_in_element',
    'clickable': 'element_to_be_clickable'
}

EXPECTED_CONDITIONS_ELEMENTS = {
    'visibility': 'visibility_of_all_elements_located',
    'presence': 'presence_of_all_elements_located',
    'text': 'text_to_be_present_in_element',
}


class BaseElements(object):

    def __init__(self, driver):
        self.element = None
        self.driver = driver

    def find(self, by, value, *args, element=None, expected_condition=None, timeout=5):
        locator = BaseElements.get_locator(by, value)
        if expected_condition:
            element = WebDriverWait(element if element else self.driver, timeout).until(
                getattr(EC, EXPECTED_CONDITIONS_ELEMENT.get(expected_condition))(locator))
        else:
            element = getattr(element if element else self.driver, 'find_element')(locator.by, locator.value)
        return element

    def find_elements(self, by, value, *args, element=None, phrase=None, expected_condition=None, timeout=10):
        def _get_elements_by_text(_elements):
            for _element in _elements:
                if phrase.lower() in _element.text.lower():
                    yield _element

        locator = BaseElements.get_locator(by, value)
        if expected_condition:
            if expected_condition != 'text':
                elements = WebDriverWait(element if element else self.driver, timeout).until(
                    getattr(EC, EXPECTED_CONDITIONS_ELEMENTS.get(expected_condition))(locator))
            else:
                elements = WebDriverWait(element if element else self.driver, timeout).until(
                    getattr(EC, EXPECTED_CONDITIONS_ELEMENTS.get(expected_condition))(locator, args[-1]))
        else:
            elements = getattr(element if element else self.driver, 'find_elements')(locator.by, locator.value)
        if phrase:
            return list(_get_elements_by_text(elements))
        else:
            return elements

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
            timeout = kwargs.get('retry_timeout', 10)
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    return func(*args, **kwargs)
                except (EC.StaleElementReferenceException, ElementClickInterceptedException) as e:
                    LOGGER.info("Error occurred:\n{e.msg}\nRetrying...")
                    print(F"Error occurred:\n{e.msg}\nRetrying...")
            raise Exception("***   element is not clickable")

        return wrapper

    # Example usage
    @retry_not_clickable
    def click_element(self, by, value, expected_condition='clickable', timeout=10, retry_timeout=10):
        self.find(by, value, expected_condition=expected_condition, timeout=timeout).click()

    def select_dropdown(self, cur, desired):
        cur_readme_selection = self.find('xpath', F"//*[text()='{cur}']", expected_condition='clickable')
        cur_readme_selection.click()
        option = self.find('xpath', F"//*[text()='{desired}']", expected_condition='clickable')
        self.driver.execute_script("arguments[0].scrollIntoView();", option)
        option.click()

    @staticmethod
    def get_value(self, element):
        return element.text

    @staticmethod
    def set_value(element, value):
        element.clear()
        element.send_keys(value)
        return None

    @staticmethod
    def get_locator(by, value):
        return Locator(by, value)
