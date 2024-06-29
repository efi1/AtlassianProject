import time

from selenium.common import TimeoutException

from src.web.clients.base_elements import BaseElements
from src.web.clients.base_page import BasePage
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select

LOGGER = logging.getLogger()
REPOSITORY = 'Repository'
PROJECT = 'Project'
REPOSITORIES = 'Repositories'
PROJECTS = 'Projects'

obj_create_desc = {"Repository": "Create a new repository", "Project": "Create a project"}
obj_validation_dec = {"Repositories": "Repository settings", "Projects": "Project settings"}


class BitBucketActivities(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = kwargs.get('url')
        self.base_elements = BaseElements(self.driver)

    @property
    def open_page(self):
        self.driver.get(self.url)

    @property
    def login(self):
        username = self.base_elements.find(By.ID, 'username', expected_condition='presence')
        username.send_keys(email_address)
        button_continue = self.base_elements.find(By.ID, 'login-submit', expected_condition='clickable')
        button_continue.click()
        passwd = self.base_elements.find(By.ID, 'password', expected_condition='clickable')
        passwd.send_keys(passwd_val)
        button_continue.click()

    @property
    def delete_repos(self) -> None:
        row_no = 1
        while True:
            self.go_resource(REPOSITORIES)
            repo_table = inst.base_elements.find(By.XPATH, F"//*[@id='profile-repositories']"
                                                           F"/div[3]/table/tbody",
                                                 expected_condition='visibility')
            if repo_table.text.startswith('No repositories'):
                break
            repo_table.click()
            get_repo = inst.base_elements.find(By.XPATH, F"//*[@id='profile-repositories']"
                                                         F"/div[3]/table/tbody/tr[{row_no}]/td[1]/div/div[2]/a",
                                               expected_condition='clickable')
            get_repo.click()
            inst.base_elements.click_element(By.XPATH,
                                             ".//div[contains(text(), 'Repository settings')]/../../../a/div/span",
                                             expected_condition='clickable', timeout=20)
            inst.base_elements.click_element(By.XPATH, ".//div/button/span[contains(text(), 'Manage repository')]",
                                             expected_condition='clickable', timeout=20)
            delete_repo = inst.base_elements.find(By.XPATH, ".//span[contains(text(), 'Delete repository')]")
            delete_repo.click()
            delete_button = inst.base_elements.find(By.XPATH, "//span[text()='Delete']")
            delete_button.click()
            row_no += 1

    @property
    def delete_projects(self):
        proj_no = 1
        while True:
            self.go_resource(PROJECTS)
            project_content = inst.base_elements.find(By.XPATH, "//table/tbody", expected_condition='visibility',
                                                      timeout=20)
            if project_content.text.startswith('No projects'):
                break
            project = inst.base_elements.find(By.XPATH, F"//div/table/tbody/tr/td[{proj_no}]/div/div/a",
                                              expected_condition='clickable')
            cur_proj = project.text
            project.click()
            inst.base_elements.click_element(By.XPATH, "//div[contains(text(), 'Project settings')]/../../div/span",
                                             expected_condition='clickable', retry_timeout=5)
            delete_project = inst.base_elements.find(By.XPATH, "//div[contains(text(), 'Delete project')]/..",
                                                     expected_condition='clickable')
            delete_project.click()
            submit_delete = inst.base_elements.find(By.XPATH, "//button/span[contains(text(), 'Delete')]",
                                                    expected_condition='clickable')
            submit_delete.click()
            inst.base_elements.click_element(By.XPATH, F"//span[contains(text(), 'Projects')]",
                                             expected_condition='clickable', timeout=10, retry_timeout=10)
            assert inst.base_elements.is_elem_removed(By.XPATH, F"//span[contains(text(), '{cur_proj}')]",
                                                      expected_condition='visibility', timeout=2, retry_timeout=10), (
                'project is not deleted')
            proj_no += 1

    @property
    def tear_down(self):
        self.delete_repos
        self.delete_projects

    def go_create(self, item):
        create_all = self.base_elements.find(By.XPATH, "//button[@id='createGlobalItem']/span[1]",
                                             expected_condition='clickable')
        create_all.click()
        get_item = self.base_elements.find(By.XPATH, F"//a[@data-testid='{item.lower()}-create-item']",
                                           expected_condition='clickable')
        get_item.click()
        self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{obj_create_desc.get(item)}')]",
                                expected_condition='visibility')

    @property
    def go_your_work(self):
        self.base_elements.click_element(By.XPATH, "//span[contains(text(), 'Your work')]",
                                         expected_condition='clickable', timeout=10, retry_timeout=10)

    @property
    def go_bitbucket(self):
        link_to_workspace = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Bitbucket')]/../../..",
                                                    expected_condition='clickable', timeout=20)
        link_to_workspace.click()

    def go_resource(self, item):
        self.go_your_work
        self.base_elements.click_element(By.XPATH, F"//span[contains(text(), '{item}')]",
                                         expected_condition='clickable', timeout=20, retry_timeout=10)

    @property
    def submit_button(self):
        submit_button = self.base_elements.find(By.XPATH, ".//button[@type='submit']").click()

    def is_item_exist(self, resource, name_arg):
        self.go_resource(resource)
        try:
            self.base_elements.find(By.XPATH, F"//a[contains(text(), '{name_arg}')]", expected_condition='presence')
            return True
        except Exception as e:
            LOGGER.info(F"Can't validate {resource}: {name_arg}, Error: {e}")
            return False

    def open_resource(self, resource, name_arg):
        self.go_resource(resource)
        self.base_elements.click_element(By.XPATH, F"//a[contains(text(), '{name_arg}')]",
                                         expected_condition='clickable', retry_timeout=5)

    def open_resource_item(self, resource, name_arg):
        try:
            self.open_resource(resource, name_arg)
            self.base_elements.find(By.XPATH, F"//div[contains(text(), '{obj_validation_dec.get(resource)}')]",
                                    expected_condition='presence')
            return True
        except Exception as e:
            LOGGER.info(F"can't open project: {e}")
            return False

    def create_project(self, proj_name_arg) -> bool:
        try:
            self.go_your_work
            self.go_create(PROJECT)
            proj_name = self.base_elements.find(By.NAME, 'name')
            proj_name.send_keys(proj_name_arg)
            self.submit_button
            self.base_elements.find(By.XPATH, "//h4[contains(text(), 'Welcome to your new project')]",
                                    expected_condition='presence', timeout=5)
        except Exception as e:
            LOGGER.info(F"project creation failed: {e}")
            return False
        return True

    def create_repo(self, project_name_arg, repo_name_arg):
        try:
            self.go_create(REPOSITORY)
            dropdown_projects = self.base_elements.find(By.XPATH, "//span[contains(text(), 'Select project')]",
                                                        expected_condition='clickable')
            dropdown_projects.click()
            select_proj = self.base_elements.find(By.XPATH, F"//span[contains(text(), '{project_name_arg}')]",
                                                  expected_condition='clickable')
            select_proj.click()
            repo_name = self.base_elements.find(By.NAME, 'name')
            repo_name.send_keys(new_repo_name)
            self.base_elements.select_dropdown('Yes, with a tutorial (for beginners)', 'No')
            self.submit_button
            self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{repo_name_arg}')]",
                                    expected_condition='presence')
        except Exception as e:
            LOGGER.info(F"repo creation failed: {e}")
            return False
        return True

    def go_branches(self, repo_name_arg):
        self.open_resource(REPOSITORIES, repo_name_arg)
        branches_link = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Branches')]/../..",
                                                expected_condition='presence', timeout=5)
        branches_link.click()

    def create_branch(self, repo_name_arg, branch_name_arg) -> bool:
        try:
            self.go_branches(repo_name_arg)
            create_br_link = self.base_elements.click_element(By.XPATH, "//span[contains(text(), 'Create branch')]",
                                                              expected_condition='clickable')
            br_text_box = self.base_elements.find(By.XPATH, "//input[@name='branchName']")
            br_text_box.send_keys(branch_name)
            self.base_elements.click_element(By.XPATH, "//button[@id='create-branch-button']/span",
                                             expected_condition='clickable', timeout=20, retry_timeout=10)
            self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{branch_name_arg}')]",
                                    expected_condition='visibility')

        except Exception as e:
            LOGGER.info(F"branch creation failed: {e.msg}")
            print(e)
            return False
        return True

    def open_branch(self, repo_name_arg, branch_name_arg):
        self.go_branches(repo_name_arg)
        cur_view = self.base_elements.find(By.XPATH, "//div[contains(@class, 'singleValue')]",
                                           expected_condition='visibility').text
        if cur_view != 'All branches':
            self.base_elements.select_dropdown(cur_view, 'All branches')
        branch_elem = self.base_elements.find(By.XPATH, F"//a[contains(text(), '{branch_name_arg}')]",
                                              expected_condition='clickable', timeout=15)
        branch_elem.click()

    def add_readme(self, repo_name_arg, branch_name_arg, filename_arg):
        try:
            self.open_branch(repo_name_arg, branch_name_arg)
            self.base_elements.find(By.XPATH, "//span[(text()='View source')]", expected_condition='clickable').click()
            self.base_elements.find(By.XPATH, F"//span[(text()='{branch_name_arg}')]", expected_condition='visibility',
                                    timeout=15)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
            self.base_elements.click_element(By.XPATH, "//button[@data-testid='repo-actions-menu--trigger']",
                                             retry_timeout=10)
            self.base_elements.find(By.XPATH, "//span[(text()='Add file')]").click()
            time.sleep(3)  # arbitrary wait due do an open issue in Bitbucket
            file_name = self.base_elements.find(By.XPATH, "//input[@id='filename']", expected_condition='presence')
            file_name.send_keys(filename_arg)
            code_mirror = self.base_elements.find(By.XPATH, "//div[@class='CodeMirror cm-s-trac']",
                                                  expected_condition='visibility')
            code_line = self.base_elements.find(By.XPATH, "//div[@class='CodeMirror-lines']", element=code_mirror,
                                                expected_condition='clickable')
            code_line.click()
            text_area = self.base_elements.find(By.CSS_SELECTOR, "textarea", element=code_mirror)
            text_area.send_keys(filename_arg)
            commit_button = self.base_elements.find(By.XPATH,
                                                    "//button[@class='save-button aui-button aui-button-primary']")
            commit_button.click()
            self.base_elements.click_element(By.XPATH, "//h2[text()='Commit changes']", expected_condition='visibility',
                                             timeout=15)
            self.base_elements.find(By.XPATH, "//div[@class='dialog-button-panel']/button").click()
            return True
        except Exception as e:
            LOGGER.info(F"add_readme failed, Error: {e}")
            return False

    def branch_drop_list(self, repo_name_arg, branch_name_arg):
        self.open_branch(repo_name_arg, branch_name_arg)
        dropdown_list = \
            self.base_elements.find_elements(By.XPATH, "//div[contains(@class,'Droplist')]/div/button/span/span",
                                             expected_condition='presence', timeout=20)[0]
        dropdown_list.click()

    def delete_branch(self, repo_name_arg, branch_name_arg):
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        self.base_elements.click_element(By.XPATH, "//span[text()='Delete branch']",
                                         expected_condition='clickable', timeout=20)
        confirm_delete = self.base_elements.find(By.XPATH, "//span[text()='Delete']",
                                                 expected_condition='clickable')
        confirm_delete.click()
        return self.confirm_deletion('self.open_branch(args[0], args[1])', repo_name_arg, branch_name_arg)

    def is_readme_exist(self, repo_name_arg, branch_name_arg, filename_arg):
        self.open_branch(repo_name_arg, branch_name_arg)
        try:
            self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']", expected_condition='presence')
            return True
        except Exception as e:
            LOGGER.info(F"{filename_arg} doesn't exist in {branch_name}, Error: {e}")
            return False

    def merge_branch(self, repo_name_arg, branch_name_arg, filename_arg):
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        self.base_elements.click_element(By.XPATH, "//span[text()='Merge']",
                                         expected_condition='clickable', timeout=20, retry_timeout=20)
        self.submit_button
        self.open_resource(REPOSITORIES, repo_name_arg)
        try:
            added_file = self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']")
            added_file.click()
            self.base_elements.find(By.XPATH, F"//h1[text()='{filename_arg}]")
            return True
        except TimeoutException:
            return False



    def confirm_deletion(self, func, *args):
        try:
            eval(func)
        except TimeoutException as e:
            LOGGER.info(F"deletion was successful - can't be found: {e}")
            return True
        return False


if __name__ == '__main__':
    url = 'https://id.atlassian.com/login'
    email_address = 'efio.at.work@gmail.com'
    passwd_val = 'aX7&oMCc1^'
    new_proj_name = 'test_proj_01'
    new_repo_name = 'test_repo_01'
    branch_name = 'test_branch_01'
    filename = 'README.md'

    inst = BitBucketActivities(url=url)
    inst.open_page
    inst.login
    inst.go_bitbucket

    # inst.tear_down

    # inst.create_project(new_proj_name)
    #

    # assert inst.open_resource_item(PROJECTS, new_proj_name) is True
    # assert inst.open_resource_item(REPOSITORIES, new_repo_name) is True
    # assert inst.is_item_exist(REPOSITORIES, new_repo_name) is True
    # assert inst.is_item_exist(PROJECTS, new_proj_name) is True

    # inst.delete_repos
    # inst.create_repo(new_proj_name, new_repo_name)
    # assert inst.delete_branch(new_repo_name, branch_name) is True
    # assert inst.create_branch(new_repo_name, branch_name) is True
    # assert inst.add_readme(new_repo_name, branch_name, filename) is True
    # assert inst.is_readme_exist(new_repo_name, branch_name, filename) is True
    assert inst.merge_branch(new_repo_name, branch_name, filename) is True

    #


    # inst.create_project_and_repo(new_proj_name, new_repo_name)

    inst.tear_down_driver
