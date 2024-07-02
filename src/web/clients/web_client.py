import time
import inspect
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
        self.password = kwargs.get('password')

    @BaseElements.alerts_handling
    def go_your_work(self):
        """
        go to the user's workspace
        :return: True if succeed False if fails
        """
        self.base_elements.find(By.XPATH, "//span[contains(text(), 'Your work')]",
                                expected_condition='clickable', timeout=10).click()

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
        passwd.send_keys(self.password)
        button_continue.click()

    @BaseElements.alerts_handling
    def logout(self):
        """
        logout Bitbucket account
        :return: return True if succeeded, False if not
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        profile_button = self.base_elements.find(By.XPATH, F"//button[contains(@data-testid, 'profile-button')]",
                                                 expected_condition='clickable', timeout=30)
        profile_button.click()
        log_out = self.base_elements.find(By.XPATH, F"//span[text()='Log out']", expected_condition='clickable')
        log_out.click()

    @BaseElements.alerts_handling
    def go_bitbucket(self):
        """ go to the home page """
        if self.base_elements.supress_time_exception(By.XPATH, "//span[@aria-label='Atlassian']", timeout=20):
            link_to_workspace = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Bitbucket')]/../../..",
                                                        expected_condition='clickable', timeout=25)
            link_to_workspace.click()
        elif not self.base_elements.supress_time_exception(By.XPATH, "//span[@aria-label='Bitbucket']",
                                                           expected_condition='presence', timeout=20):
            self.relogin

    @BaseElements.alerts_handling
    def tear_down_resources(self, proj_name_arg, repo_name_arg):
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.delete_repos(repo_name_arg)
        self.delete_projects(proj_name_arg)

    @BaseElements.alerts_handling
    def go_resource(self, item: str):
        """
        view the user's projects or repositories
        :param item: PROJECTS or REPOSITORIES
        :return: True if succeed False if fails
        """
        self.base_elements.click_element(By.XPATH, F"//span[contains(text(), '{item}')]")

    @BaseElements.alerts_handling
    def delete_repos(self, repo_name_arg):
        """ delete all user's repos. """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_resource(REPOSITORIES) is True, 'failed to navigate to repositories page'
        if self.base_elements.click_table_row_element(repo_name_arg):
            self.base_elements.click_element(By.XPATH,
                                             ".//div[contains(text(), 'Repository settings')]/../../../a/div/span")
            self.base_elements.click_element(By.XPATH, ".//div/button/span[contains(text(), 'Manage repository')]")
            delete_repo = self.base_elements.find(By.XPATH, ".//span[contains(text(), 'Delete repository')]")
            delete_repo.click()
            delete_button = self.base_elements.find(By.XPATH, "//span[text()='Delete']")
            delete_button.click()

    @BaseElements.alerts_handling
    def delete_projects(self, project_name_arg):
        """ delete all user's projects """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_resource(PROJECTS) is True, 'failed to navigate to projects page'
        if self.base_elements.click_table_row_element(project_name_arg):
            self.base_elements.click_element(By.XPATH, "//div[contains(text(), 'Project settings')]/../../div/span")
            delete_project = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Delete project')]/..")
            delete_project.click()
            submit_delete = self.base_elements.find(By.XPATH, "//button/span[contains(text(), 'Delete')]",
                                                    expected_condition='clickable')
            submit_delete.click()
            self.base_elements.click_element(By.XPATH, F"//span[contains(text(), 'Projects')]")
            assert self.base_elements.is_elem_removed(By.XPATH, F"//span[contains(text(), '{project_name_arg}')]",
                                                      expected_condition='visibility', timeout=3, retry_timeout=20), (
                'project is not deleted')

    @BaseElements.alerts_handling
    def go_create(self, item: str):
        """
        select from menu the relevant option for creating a project or a repo.
        :param item: whether it is a PROJECT or a REPOSITORY
        """
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

    @BaseElements.alerts_handling
    def submit_button(self):
        """
        click on submit button
        """
        self.base_elements.find(By.XPATH, ".//button[@type='submit']", expected_condition='clickable').click()

    @BaseElements.alerts_handling
    def is_item_exist(self, resource: str, name_arg: str):
        """
        check if a project or a repo exists, by their names.
        :param resource: REPOSITORIES or PROJECTS
        :param name_arg: repo or project name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_resource(resource) is True, F"failed to navigate to {resource} page"
        self.base_elements.find(By.XPATH, F"//a[contains(text(), '{name_arg}')]", expected_condition='presence')

    @BaseElements.alerts_handling
    def open_resource(self, resource, name_arg):
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}; opening {resource}: {name_arg}")
        self.go_resource(resource)
        self.base_elements.click_element(By.XPATH, F"//a[contains(text(), '{name_arg}')]")

    @BaseElements.alerts_handling
    def open_resource_item(self, resource: str, name_arg: str):
        """
        open repository or project by their names
        :param resource: whether a PROJECT or a REPOSITORY
        :param name_arg: the repository's or project name
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}; opening {resource}: {name_arg}")
        obj_validation_dec = {"Repositories": "Repository settings", "Projects": "Project settings"}
        self.open_resource(resource, name_arg)
        self.base_elements.find(By.XPATH, F"//div[contains(text(), '{obj_validation_dec.get(resource)}')]",
                                expected_condition='presence')

    @BaseElements.alerts_handling
    def create_project(self, proj_name_arg: str, proj_key_arg: str):
        """
        create a new project by a given name
        :param proj_key_arg: project's key
        :param proj_name_arg: project name
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.go_create(PROJECT)
        proj_name = self.base_elements.find(By.NAME, 'name')
        proj_name.send_keys(proj_name_arg)
        proj_key = self.base_elements.find(By.XPATH, "//input[@name='key']")
        self.base_elements.set_value(proj_key, proj_key_arg)
        assert self.submit_button() is True, "submit button in a project creation is missing or isn't clickable"
        self.base_elements.find(By.XPATH, "//h4[contains(text(), 'Welcome to your new project')]",
                                expected_condition='presence', timeout=5)

    @BaseElements.alerts_handling
    def create_repo(self, project_name_arg: str, repo_name_arg: str):
        """
        create a new repository by a given name
        :param project_name_arg: the project which the repo is created in.
        :param repo_name_arg: the repo name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
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
        assert self.submit_button() is True, "submit button in a repo creation is missing or isn't clickable"
        self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{repo_name_arg}')]",
                                expected_condition='presence')

    @BaseElements.alerts_handling
    def go_branches(self, repo_name_arg: str):
        """
        open branches' list of a given repo
        :param repo_name_arg:  the repo name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_resource(REPOSITORIES, repo_name_arg)
        branches_link = self.base_elements.find(By.XPATH, "//div[contains(text(), 'Branches')]/../..",
                                                expected_condition='presence', timeout=5)
        branches_link.click()

    @BaseElements.alerts_handling
    def create_branch(self, repo_name_arg: str, branch_name_arg: str):
        """
        create a branch for a given repo.
        :param repo_name_arg: the repo name.
        :param branch_name_arg: the branch name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_branches(repo_name_arg) is True, F"failed to navigate branches"
        self.base_elements.find(By.XPATH, "//span[contains(text(), 'Create branch')]",
                                expected_condition='clickable').click()
        br_text_box = self.base_elements.find(By.XPATH, "//input[@name='branchName']")
        br_text_box.send_keys(branch_name_arg)
        self.base_elements.click_element(By.XPATH, "//button[@id='create-branch-button']/span")
        self.base_elements.find(By.XPATH, F"//h1[contains(text(), '{branch_name_arg}')]",
                                expected_condition='visibility')

    @BaseElements.alerts_handling
    def open_branch(self, repo_name_arg: str, branch_name_arg: str):
        """
        open a brunch by a given branch name.
        :param repo_name_arg:
        :param branch_name_arg:
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        assert self.go_branches(repo_name_arg) is True, "failed to navigate branches"
        cur_view = self.base_elements.find(By.XPATH, "//div[contains(@class, 'singleValue')]",
                                           expected_condition='visibility').text
        if cur_view != 'All branches':
            self.base_elements.select_dropdown(cur_view, 'All branches')
        branch_elem = self.base_elements.find(By.XPATH, F"//a[contains(text(), '{branch_name_arg}')]",
                                              expected_condition='clickable', timeout=15)
        branch_elem.click()

    @BaseElements.alerts_handling
    def add_readme(self, repo_name_arg, branch_name_arg, filename_arg):
        """
        add a readme file to a given branch name.
        :param repo_name_arg: the repo of which the branch belong to.
        :param branch_name_arg: the branch name.
        :param filename_arg: the file's name to be added to the branch (README.md)
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_branch(repo_name_arg, branch_name_arg)
        self.base_elements.find(By.XPATH, "//span[(text()='View source')]", expected_condition='clickable').click()
        self.base_elements.find(By.XPATH, F"//span[(text()='{branch_name_arg}')]", expected_condition='visibility',
                                timeout=15)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        self.base_elements.find(By.XPATH, "//button[@data-testid='repo-actions-menu--trigger']",
                                expected_condition='clickable').click()
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
        self.base_elements.find(By.XPATH, "//h2[text()='Commit changes']", expected_condition='clickable').click()
        self.base_elements.find(By.XPATH, "//div[@class='dialog-button-panel']/button").click()

    @BaseElements.alerts_handling
    def branch_drop_list(self, repo_name_arg: str, branch_name_arg: str):
        """
        open branch manage list (to view the action which can be performed on a branch - like delete or merge)
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_branch(repo_name_arg, branch_name_arg)
        self.base_elements.find(By.XPATH, "//div[contains(@class,'Droplist')]/div/button/span/span",
                                expected_condition='clickable', timeout=10).click()

    @BaseElements.alerts_handling
    def delete_branch(self, repo_name_arg: str, branch_name_arg: str):
        """
        delete a branch by its name and the repo of which it is associated with.
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        self.base_elements.find(By.XPATH, "//span[text()='Delete branch']",
                                expected_condition='clickable', timeout=10).click()
        confirm_delete = self.base_elements.find(By.XPATH, "//span[text()='Delete']",
                                                 expected_condition='clickable')
        confirm_delete.click()
        self.open_branch(repo_name_arg, branch_name_arg)

    @BaseElements.alerts_handling
    def is_readme_exist(self, repo_name_arg: str, branch_name_arg: str, filename_arg: str = 'README.md'):
        """
        verify that a readme file was added to a branch
        :param repo_name_arg: repo name.
        :param branch_name_arg: branch name.
        :param filename_arg: usually it is README.md .
        """
        LOGGER.info(F"++++ in {inspect.currentframe().f_code.co_name}....")
        self.open_branch(repo_name_arg, branch_name_arg)
        self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']", expected_condition='presence')

    @BaseElements.alerts_handling
    def merge_branch(self, repo_name_arg, branch_name_arg, filename_arg):
        """
        merge a branch's content with its repo
        :param repo_name_arg:
        :param branch_name_arg:
        :param filename_arg: the filename which exist in the branch.
        """
        LOGGER.info(F"++++++   in {inspect.currentframe().f_code.co_name}...")
        self.branch_drop_list(repo_name_arg, branch_name_arg)
        time.sleep(3)  # due to loading issues
        self.base_elements.find(By.XPATH, "//span[text()='Merge']",
                                expected_condition='clickable', timeout=10).click()
        assert self.submit_button() is True, "submit button in a branch creation is missing or isn't clickable"
        self.open_resource(REPOSITORIES, repo_name_arg)
        added_file = self.base_elements.find(By.XPATH, F"//span[text()='{filename_arg}']",
                                             expected_condition='clickable')
        added_file.click()
        self.base_elements.find(By.XPATH, F"//p[text()='{filename_arg}']", expected_condition='presence')


if __name__ == '__main__':
    url = 'https://id.atlassian.com/login'
    email_address = 'efio.at.work@gmail.com'
    passwd_val = 'aX7&oMCc1^'
    new_proj_name = 'test_proj_01'
    new_proj_key = 'PRJ'
    new_repo_name = 'test_repo_01'
    branch_name = 'test_branch_01'
    filename = 'README.md'

    inst = BitBucketActivities(url=url)
    inst.open_page
    inst.login(email_address, passwd_val)
    inst.logout()
    inst.go_bitbucket()
    assert inst.delete_branch(new_repo_name, branch_name) is True
    inst.delete_repos
    inst.tear_down_resources(new_proj_name, new_repo_name)
    assert inst.create_project(new_proj_name) is True
    assert inst.create_repo(new_proj_name, new_repo_name) is True
    assert inst.open_resource_item(PROJECTS, new_proj_name, new_proj_key) is True
    assert inst.open_resource_item(REPOSITORIES, new_repo_name) is True
    assert inst.is_item_exist(REPOSITORIES, new_repo_name) is True
    assert inst.is_item_exist(PROJECTS, new_proj_name) is True
    assert inst.create_branch(new_repo_name, branch_name) is True
    assert inst.add_readme(new_repo_name, branch_name, filename) is True
    assert inst.is_readme_exist(new_repo_name, branch_name, filename) is True
    assert inst.merge_branch(new_repo_name, branch_name, filename) is True

    inst.tear_down_driver
