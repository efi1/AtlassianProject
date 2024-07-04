import time
import logging
from selenium.common import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from src.web.clients.locator import Locator
from selenium.webdriver.common.by import By


LOGGER = logging.getLogger()

EXPECTED_CONDITIONS_ELEMENT = \
    {
        'visibility': 'visibility_of_element_located',
        'presence': 'presence_of_element_located',
        'text': 'text_to_be_present_in_element',
        'clickable': 'element_to_be_clickable'
    }

EXPECTED_CONDITIONS_ELEMENTS = \
    {
        'visibility': 'visibility_of_all_elements_located',
        'presence': 'presence_of_all_elements_located',
        'text': 'text_to_be_present_in_element',
    }


class BaseElements(object):

    def __init__(self, driver):
        self.element = None
        self.driver = driver

    def find(self, by, value, element=None, expected_condition=None, timeout=5) -> object:
        """
        Add a waiting functionality (with expected condition) to the 'find_element' function.
        :param by: locator
        :param value: searched value
        :param element: searching within a given element (instead os the webdriver)
        :param expected_condition: element object
        :param timeout: timeout to wait for the expected_condition to be fulfilled
        :return: the found element
        """
        locator = BaseElements.get_locator(by, value)
        if expected_condition:
            element = WebDriverWait(element if element else self.driver, timeout).until(
                getattr(EC, EXPECTED_CONDITIONS_ELEMENT.get(expected_condition))(locator))
        else:
            element = getattr(element if element else self.driver, 'find_element')(locator.by, locator.value)
        return element

    def find_elements(self, by, value, *args, element=None, phrase=None, expected_condition=None, timeout=10):
        locator = BaseElements.get_locator(by, value)
        if expected_condition:
            elements = WebDriverWait(element if element else self.driver, timeout).until(
                getattr(EC, EXPECTED_CONDITIONS_ELEMENTS.get(expected_condition))(locator))
        else:
            elements = getattr(element if element else self.driver, 'find_elements')(locator.by, locator.value)
        return elements

    @staticmethod
    def retry_removed_element(func) -> bool:
        """
        Validate that a resource (i.e. project, repo) was deleted
        :param func: the wrapped function
        :return: True if removed successfully, False if not.
        """
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
    def retry_not_clickable(func) -> object:
        """
        it retries func exec when StaleElementReferenceException or ElementClickInterceptedException occur.
        :param func: the wrapped function.
        :return: the function execution result.
        """
        def wrapper(*args, **kwargs):
            counter = 0
            retries = kwargs.get('retries', 5)
            while counter <= retries:
                try:
                    return func(*args, **kwargs)
                except (EC.StaleElementReferenceException, ElementClickInterceptedException) as e:
                    LOGGER.info(F"Error occurred:\n{e.msg}\nRetrying...")
            raise Exception("***   element is not clickable")

        return wrapper

    @retry_not_clickable
    def click_element(self, by, value, expected_condition='clickable', timeout=5, retries=5):
        self.find(by, value, expected_condition=expected_condition, timeout=timeout).click()

    def select_dropdown(self, cur, desired) -> None:
        """
        handle area text box - drop down table
        :param cur: the current state or text which is set
        :param desired: the required text to be set
        :return: no returns, only select the required option
        """
        cur_readme_selection = self.find('xpath', F"//*[text()='{cur}']", expected_condition='clickable')
        cur_readme_selection.click()
        option = self.find('xpath', F"//*[text()='{desired}']", expected_condition='clickable')
        self.driver.execute_script("arguments[0].scrollIntoView();", option)
        option.click()

    @staticmethod
    def get_locator(by, value):
        return Locator(by, value)

    @staticmethod
    def set_value(element, value):
        element.clear()
        element.send_keys(value)
        return None

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

    @staticmethod
    def alerts_handling(func) -> bool:
        """
        execute a given function and return True on Success, False on a failure
        it also overcomes alerts like unexpected login prompt and other unexpected alert.
        if login prompt arisen, it re-login.
        :param func: the function which is decorated with this function.
        :return: True on Success, False on a failure
        """
        def wrapper(self, *args):
            try:
                func(self, *args)
            except TimeoutException:
                if self.base_elements.supress_time_exception(By.ID, 'login-submit', expected_condition='clickable',
                                                             timeout=2):
                    LOGGER.info(F"an unexpected login prompt occurred")
                    self.login
                elif self.base_elements.supress_time_exception(By.XPATH, "//h3[text()='Something went wrong']", expected_condition='presence', timeout=3):
                    LOGGER.info(F"an unexpected alert occurred, refreshing page...")
                    self.driver.refresh()
                elif self.base_elements.supress_time_exception(By.XPATH, "//h1[contains(text()='Repository not found')]", expected_condition='presence', timeout=3):
                    LOGGER.info(F"an unexpected alert occurred, refreshing page...")
                    self.driver.refresh()
                elif self.base_elements.supress_time_exception(By.XPATH, "//a[@data-label='Get it free']", expected_condition='presence', timeout=3):
                    LOGGER.info(F"an unexpected alert occurred, refreshing page...")
                    self.go_back
                else:
                    LOGGER.info(F"Error, called by: {func.__name__}, args: {args}")
                    return False
                func(self, *args)
            return True

        return wrapper

    def click_table_row_element(self, resource_name: str) -> bool:
        """
        search for a requested resource (repo/project) -> if found one, click and return True
        :param resource_name:
        :return: True/False if the requested resource found
        """
        tb_row_elements = self.find_elements(By.XPATH, "//td/div/div/a", expected_condition='presence')
        for elem in tb_row_elements:
            if elem.text.startswith(resource_name):
                elem.click()
                return True
        return False

