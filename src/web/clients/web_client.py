import time
import inspect
from selenium.common import TimeoutException

from src.web.clients.base_elements import BaseElements
from src.web.clients.base_page import BasePage
from selenium.webdriver.common.by import By
import logging

LOGGER = logging.getLogger()

REPOSITORY = 'Repository'
PROJECT = 'Project'
REPOSITORIES = 'Repositories'
PROJECTS = 'Projects'


class BitBucketActivities(BasePage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = kwargs.get('url')
        self.base_elements = BaseElements(self.driver)
        self.email = kwargs.get('email')
        self.pswd = kwargs.get('passwd')

    @property
    def open_page(self):
        self.driver.get(self.url)

    @property
    def login(self) -> None:
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        username = self.base_elements.find(By.ID, 'username', expected_condition='presence')
        username.send_keys(self.email)
        button_continue = self.base_elements.find(By.ID, 'login-submit', expected_condition='clickable')
        button_continue.click()
        passwd = self.base_elements.find(By.ID, 'password', expected_condition='clickable')
        passwd.send_keys(self.pswd)
        button_continue.click()
        self.go_bitbucket

    @property
    def logout(self) -> bool:
        """
        logout Bitbucket account
        :return: return True if succeeded, False if not
        """
        try:
            LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
            profile_button = self.base_elements.find(By.XPATH, F"//button[contains(@data-testid, 'profile-button')]",
                                                     expected_condition='clickable', timeout=30)
            profile_button.click()
            log_out = self.base_elements.find(By.XPATH, F"//span[text()='Log out']", expected_condition='clickable')
            log_out.click()
        except TimeoutException:
            LOGGER.info('logging out from Bitbucket failed')
            return False
        return True

    @property
    def relogin(self):
        if not self.base_elements.supress_time_exception(By.ID, 'ProductHeading', expected_condition='presence'):
            self.login
        else:
            print()

    @property
    def go_bitbucket(self) -> None:
        """ go to the home page """
        if self.base_elements.supress_time_exception(By.XPATH, "//span[@aria-label='Atlassian']", timeout=20):
            link_to_workspace = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Bitbucket')]/../../..",
                                                        expected_condition='clickable', timeout=25)
            link_to_workspace.click()
        elif not self.base_elements.supress_time_exception(By.XPATH, "//span[@aria-label='Bitbucket']",
                                                           expected_condition='presence', timeout=20):
            self.relogin

    @property
    def tear_down_resources(self):
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.delete_repos
        self.delete_projects

    @property
    def go_your_work(self) -> bool:
        """
        go to the user's workspace
        :return: True if succeed False if fails
        """
        try:
            self.base_elements.click_element(By.XPATH, "//span[contains(text(), 'Your work')]",
                                             expected_condition='clickable', timeout=5, retry_timeout=30)
        except TimeoutException as e:
            LOGGER.info(F"couldn't navigate to workspace page")
            return False
        return True

    def go_resource(self, item: str) -> None:
        """
        view the user's projects or repositories
        :param item: PROJECTS or REPOSITORIES
        :return: True if succeed False if fails
        """
        try:

            assert self.go_your_work is True, F"failed to navigate to workspace"
            self.base_elements.click_element(By.XPATH, F"//span[contains(text(), '{item}')]",
                                             expected_condition='clickable', timeout=5, retry_timeout=30)
        except Exception as e:
            LOGGER.info(F"failed to navigate to {item} page")
            return False
        return True

    @property
    def delete_repos(self) -> None:
        """ delete all user's repos. """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        row_no = 1
        while True:
            assert self.go_resource(REPOSITORIES) is True, 'failed to navigate to repositories page'
            repo_table = self.base_elements.find(By.XPATH, F"//*[@id='profile-repositories']"
                                                           F"/div[3]/table/tbody",
                                                 expected_condition='visibility', timeout=25)
            if repo_table.text.startswith('No repositories'):
                break
            repo_table.click()
            get_repo = self.base_elements.find(By.XPATH, F"//*[@id='profile-repositories']"
                                                         F"/div[3]/table/tbody/tr[{row_no}]/td[1]/div/div[2]/a",
                                               expected_condition='clickable')
            get_repo.click()
            self.base_elements.click_element(By.XPATH,
                                             ".//div[contains(text(), 'Repository settings')]/../../../a/div/span",
                                             expected_condition='clickable')
            self.base_elements.click_element(By.XPATH, ".//div/button/span[contains(text(), 'Manage repository')]",
                                             expected_condition='clickable')
            delete_repo = self.base_elements.find(By.XPATH, ".//span[contains(text(), 'Delete repository')]")
            delete_repo.click()
            delete_button = self.base_elements.find(By.XPATH, "//span[text()='Delete']")
            delete_button.click()
            row_no += 1

    @property
    def delete_projects(self) -> None:
        """ delete all user's projects """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        proj_no = 1
        while True:
            assert self.go_resource(PROJECTS) is True, 'failed to navigate to projects page'
            project_content = self.base_elements.find(By.XPATH, "//table/tbody", expected_condition='visibility',
                                                      timeout=20)
            if project_content.text.startswith('No projects'):
                break
            project = self.base_elements.find(By.XPATH, F"//div/table/tbody/tr/td[{proj_no}]/div/div/a",
                                              expected_condition='clickable')
            cur_proj = project.text
            project.click()
            self.base_elements.click_element(By.XPATH, "//div[contains(text(), 'Project settings')]/../../div/span",
                                             expected_condition='clickable', retry_timeout=5)
            delete_project = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Delete project')]/..",
                                                     expected_condition='clickable')
            delete_project.click()
            submit_delete = self.base_elements.find(By.XPATH, "//button/span[contains(text(), 'Delete')]",
                                                    expected_condition='clickable')
            submit_delete.click()
            self.base_elements.click_element(By.XPATH, F"//span[contains(text(), 'Projects')]",
                                             expected_condition='clickable', timeout=5, retry_timeout=20)
            assert self.base_elements.is_elem_removed(By.XPATH, F"//span[contains(text(), '{cur_proj}')]",
                                                      expected_condition='visibility', timeout=3, retry_timeout=20), (
                'project is not deleted')
            proj_no += 1

    def go_create(self, item: str) -> bool:
        """
        select from menu the relevant option for creating a project or a repo.
        :param item: whether it is a PROJECT or a REPOSITORY
        :return: True on success, False on failure
        """
        try:
            obj_create_desc = {"Repository": "Create a new repository", "Project": "Create a project"}
            LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
            create_all = self.base_elements.find(By.XPATH, "//button[@id='createGlobalItem']/span[1]",
                                                 expected_condition='clickable')
            create_all.click()
            get_item = self.base_elements.find(By.XPATH, F"//a[@data-testid='{item.lower()}-create-item']",
                                               expected_condition='clickable')
            get_item.click()
            self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{obj_create_desc.get(item)}')]",
                                    expected_condition='visibility')
        except TimeoutException:
            LOGGER.info(F"could not navigate to creation page of {item}")
            return False
        return True

    @property
    def submit_button(self) -> bool:
        """
        Click on submit button
        :return: True on success, False on failure
        """
        try:
            self.base_elements.click_element(By.XPATH, ".//button[@type='submit']")
        except TimeoutException as e:
            LOGGER.info(F"failed to click on Submit button, Error:\n{e.msg}")
            return False
        return True

    def is_item_exist(self, resource: str, name_arg: str) -> bool:
        """
        check if a project or a repo exists, by their names.
        :param resource: REPOSITORIES or PROJECTS
        :param name_arg: repo or project name.
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_resource(resource) is True, F"failed to navigate to {resource} page"
        try:
            self.base_elements.find(By.XPATH, F"//a[contains(text(), '{name_arg}')]", expected_condition='presence')
            return True
        except Exception as e:
            LOGGER.info(F"Can't validate {resource}: {name_arg}, Error: {e}")
            return False

    def open_resource(self, resource, name_arg):
        try:
            LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}; opening {resource}: {name_arg}")
            self.go_resource(resource)
            self.base_elements.click_element(By.XPATH, F"//a[contains(text(), '{name_arg}')]",
                                             expected_condition='clickable', retry_timeout=20)
        except Exception as e:
            LOGGER.info(F"Can't open {resource}: {name_arg}, Error: {e}")
            return False
        return True

    def open_resource_item(self, resource: str, name_arg: str) -> bool:
        """
        open repository or project by their names
        :param resource: whether a PROJECT or a REPOSITORY
        :param name_arg: the repository's or project name
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}; opening {resource}: {name_arg}")
        obj_validation_dec = {"Repositories": "Repository settings", "Projects": "Project settings"}
        try:
            self.open_resource(resource, name_arg)
            self.base_elements.find(By.XPATH, F"//div[contains(text(), '{obj_validation_dec.get(resource)}')]",
                                    expected_condition='presence')
            return True
        except Exception as e:
            LOGGER.info(F"can't open project: {e}")
            return False

    def create_project(self, proj_name_arg: str) -> bool:
        """
        create a new project by a given name
        :param proj_name_arg: project name
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_your_work is True, F"failed to navigate to workspace"
        assert self.go_create(PROJECT) is True, F"failed to create a project"
        try:
            proj_name = self.base_elements.find(By.NAME, 'name')
            proj_name.send_keys(proj_name_arg)
            assert self.submit_button is True, "submit button in a project creation is missing or isn't clickable"
            self.base_elements.find(By.XPATH, "//h4[contains(text(), 'Welcome to your new project')]",
                                    expected_condition='presence', timeout=5)
            return True
        except (TimeoutException, AssertionError) as e:
            LOGGER.info(F"project creation failed: {e}")
            return False

    def create_repo(self, project_name_arg: str, repo_name_arg: str) -> bool:
        """
        create a new repository by a given name
        :param project_name_arg: the project which the repo is created in.
        :param repo_name_arg: the repo name.
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        try:
            assert self.go_create(REPOSITORY) is True, F"failed to create a repo"
            dropdown_projects = self.base_elements.find(By.XPATH, "//span[contains(text(), 'Select project')]",
                                                        expected_condition='clickable')
            dropdown_projects.click()
            select_proj = self.base_elements.find(By.XPATH, F"//span[contains(text(), '{project_name_arg}')]",
                                                  expected_condition='clickable')
            select_proj.click()
            repo_name = self.base_elements.find(By.NAME, 'name')
            repo_name.send_keys(repo_name_arg)
            self.base_elements.select_dropdown('Yes, with a tutorial (for beginners)', 'No')
            assert self.submit_button is True, "submit button in a repo creation is missing or isn't clickable"
            self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{repo_name_arg}')]",
                                    expected_condition='presence')
        except Exception as e:
            LOGGER.info(F"repo creation failed: {e}")
            if self.base_elements.supress_time_exception(By.XPATH, "//h1[text()='Create a new repository']"):
                self.base_elements.go_back
            return False
        return True

    def go_branches(self, repo_name_arg: str) -> bool:
        """
        open branches' list of a given repo
        :param repo_name_arg:  the repo name.
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        try:
            self.open_resource(REPOSITORIES, repo_name_arg)
            branches_link = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Branches')]/../..",
                                                    expected_condition='presence', timeout=5)
            branches_link.click()
        except TimeoutException:
            LOGGER.info(F"failed to navigate branches with in repo: {repo_name_arg}")
            return False
        return True

    def create_branch(self, repo_name_arg: str, branch_name_arg: str) -> bool:
        """
        create a branch for a given repo.
        :param repo_name_arg: the repo name.
        :param branch_name_arg: the branch name.
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        try:
            assert self.go_branches(repo_name_arg) is True, F"failed to navigate branches"
            self.base_elements.click_element(By.XPATH, "//span[contains(text(), 'Create branch')]",
                                             expected_condition='clickable')
            br_text_box = self.base_elements.find(By.XPATH, "//input[@name='branchName']")
            br_text_box.send_keys(branch_name_arg)
            self.base_elements.click_element(By.XPATH, "//button[@id='create-branch-button']/span",
                                             expected_condition='clickable', timeout=5, retry_timeout=20)
            self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{branch_name_arg}')]",
                                    expected_condition='visibility')
        except Exception as e:
            LOGGER.info(F"branch creation failed: {e.msg}")
            return False
        return True

    def open_branch(self, repo_name_arg: str, branch_name_arg: str) -> bool:
        """
        open a brunch by a given branch name.
        :param repo_name_arg:
        :param branch_name_arg:
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_branches(repo_name_arg) is True, "failed to navigate branches"
        try:
            cur_view = self.base_elements.find(By.XPATH, "//div[contains(@class, 'singleValue')]",
                                               expected_condition='visibility').text
            if cur_view != 'All branches':
                self.base_elements.select_dropdown(cur_view, 'All branches')
            branch_elem = self.base_elements.find(By.XPATH, F"//a[contains(text(), '{branch_name_arg}')]",
                                                  expected_condition='clickable', timeout=15)
            branch_elem.click()
        except Exception as e:
            LOGGER.info(F"opening brunch failed: {e}")
            return False
        return True

    def add_readme(self, repo_name_arg, branch_name_arg, filename_arg):
        """
        add a readme file to a given branch name.
        :param repo_name_arg: the repo of which the branch belong.
        :param branch_name_arg: the branch name.
        :param filename_arg: the file's name to be added to the branch (README.md)
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        try:
            self.open_branch(repo_name_arg, branch_name_arg)
            self.base_elements.find(By.XPATH, "//span[(text()='View source')]", expected_condition='clickable').click()
            self.base_elements.find(By.XPATH, F"//span[(text()='{branch_name_arg}')]", expected_condition='visibility',
                                    timeout=15)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
            self.base_elements.click_element(By.XPATH, "//button[@data-testid='repo-actions-menu--trigger']")
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
            self.base_elements.click_element(By.XPATH, "//h2[text()='Commit changes']")
            self.base_elements.find(By.XPATH, "//div[@class='dialog-button-panel']/button").click()
            return True
        except Exception as e:
            LOGGER.info(F"add_readme failed, Error: {e}")
            return False

    def branch_drop_list(self, repo_name_arg: str, branch_name_arg: str) -> None:
        """
        open branch manage list (to view the action which can be performed on a branch - like delete or merge)
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_branch(repo_name_arg, branch_name_arg)
        self.base_elements.click_element(By.XPATH, "//div[contains(@class,'Droplist')]/div/button/span/span",
                                         expected_condition='clickable', timeout=10, retry_timeout=30)

    def delete_branch(self, repo_name_arg: str, branch_name_arg: str) -> bool:
        """
        delete a branch by its name and the repo of which it is associated with.
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        self.base_elements.click_element(By.XPATH, "//span[text()='Delete branch']",
                                         expected_condition='clickable', timeout=10, retry_timeout=30)
        confirm_delete = self.base_elements.find(By.XPATH, "//span[text()='Delete']",
                                                 expected_condition='clickable')
        confirm_delete.click()
        try:
            self.open_branch(repo_name_arg, branch_name_arg)
        except TimeoutException as e:
            LOGGER.info(F"deletion was successful - can't be found: {e}")
            return True
        return False

    def is_readme_exist(self, repo_name_arg: str, branch_name_arg: str, filename_arg: str = 'README.md'):
        """
        verify that a readme file was added to a branch
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        :param filename_arg: usually it is README.md .
        :return: True if succeeded, False if failed
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_branch(repo_name_arg, branch_name_arg)
        try:
            self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']", expected_condition='presence')
            return True
        except TimeoutException as e:
            LOGGER.info(F"{filename_arg} doesn't exist in {branch_name_arg}, Error: {e}")
            return False

    def merge_branch(self, repo_name_arg, branch_name_arg, filename_arg) -> bool:
        """
        merge a branch's content with its repo
        :param repo_name_arg:
        :param branch_name_arg:
        :param filename_arg: the filename which exist in the branch.
        :return: True if the README file was merged into the repo successfully, else False
        """
        LOGGER.info(F"++++++   in {inspect.currentframe().f_code.co_name}...")
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        time.sleep(3)  # due to loading issues
        self.base_elements.click_element(By.XPATH, "//span[text()='Merge']",
                                         expected_condition='visibility', timeout=6, retry_timeout=30)
        assert self.submit_button is True, "submit button in a branch creation is missing or isn't clickable"
        self.open_resource(REPOSITORIES, repo_name_arg)
        try:
            added_file = self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']",
                                                 expected_condition='clickable')
            added_file.click()
            self.base_elements.find(By.XPATH, F"//p[text()='{filename_arg}']", expected_condition='presence')
            return True
        except TimeoutException:
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
    inst.login(email_address, passwd_val)
    inst.logout

    inst.go_bitbucket

    # assert inst.delete_branch(new_repo_name, branch_name) is True
    # inst.delete_repos
    inst.tear_down_resources
    assert inst.create_project(new_proj_name) is True
    assert inst.create_repo(new_proj_name, new_repo_name) is True
    assert inst.open_resource_item(PROJECTS, new_proj_name) is True
    assert inst.open_resource_item(REPOSITORIES, new_repo_name) is True
    assert inst.is_item_exist(REPOSITORIES, new_repo_name) is True
    assert inst.is_item_exist(PROJECTS, new_proj_name) is True

    assert inst.create_branch(new_repo_name, branch_name) is True
    assert inst.add_readme(new_repo_name, branch_name, filename) is True
    assert inst.is_readme_exist(new_repo_name, branch_name, filename) is True
    assert inst.merge_branch(new_repo_name, branch_name, filename) is True

    inst.tear_down_driver
