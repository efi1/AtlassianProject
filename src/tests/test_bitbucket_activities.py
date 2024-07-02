import logging

LOGGER = logging.getLogger()


def test_exercise_scenario(web_client, tests_data, clean_workspace):
    LOGGER.info('Create a project in Bitbucket')
    res = web_client.create_project(tests_data.new_proj_name, tests_data.new_proj_key)
    assert res is True, F"fail to create a project: {tests_data.new_proj_name}"

    LOGGER.info(F"Verify the project's existence")
    res = web_client.is_item_exist(tests_data.PROJECTS, tests_data.new_proj_name)
    assert res is True, F"verification failed, project: {tests_data.new_proj_name}"

    LOGGER.info('Navigate to a specific project in Bitbucket')
    res = web_client.open_resource(tests_data.PROJECTS, tests_data.new_proj_name)
    assert res is True, F"fail to open a project: {tests_data.new_proj_name}"

    LOGGER.info('Create a new repository within the project')
    res = web_client.create_repo(tests_data.new_proj_name, tests_data.new_repo_name)
    assert res is True, F"fail to create a repo: {tests_data.new_repo_name}"

    LOGGER.info(F"Verify the repository's existence")
    res = web_client.is_item_exist(tests_data.REPOSITORIES, tests_data.new_repo_name)
    assert res is True, F"verification failed, repo: {tests_data.new_repo_name}"

    LOGGER.info(F"Create a new branch in the repository")
    res = web_client.create_branch(tests_data.new_repo_name, tests_data.branch_name)
    assert res is True, F"fail to create a branch: {tests_data.branch_name}"

    LOGGER.info(F"Add a README file to the branch")
    res = web_client.add_readme(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to add a README file to the branch: {tests_data.branch_name}, filename: {tests_data.filename}"

    LOGGER.info(F"Verify the presence of the README file")
    res = web_client.is_readme_exist(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to verify the presence of the README file: {tests_data.branch_name}, filename: {tests_data.filename}"

    LOGGER.info(F"Merge the branch into the main repository branch")
    res = web_client.merge_branch(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, (F"fail merge the branch into the main repository branch: {tests_data.branch_name}, "
                         F"repo name: {tests_data.new_repo_name}")

    LOGGER.info(F"Log out from Bitbucket")
    assert web_client.logout() is True, 'failed to logout'


def test_negative_verify_non_exist_file_in_branch(web_client, tests_data, clean_workspace):

    LOGGER.info('Create a project in Bitbucket')
    res = web_client.create_project(tests_data.new_proj_name, tests_data.new_proj_key)
    assert res is True, F"fail to create a project: {tests_data.new_proj_name}"

    LOGGER.info('Create a new repository within the project')
    res = web_client.create_repo(tests_data.new_proj_name, tests_data.new_repo_name)
    assert res is True, F"fail to create a repo: {tests_data.new_repo_name}"

    LOGGER.info(F"Create a new branch in the repository")
    res = web_client.create_branch(tests_data.new_repo_name, tests_data.branch_name)
    assert res is True, F"fail to create a branch: {tests_data.branch_name}"

    LOGGER.info(F"Add a README file to the branch")
    res = web_client.add_readme(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to add a README file to the branch: {tests_data.branch_name}, filename: {tests_data.filename}"

    LOGGER.info(F"Verify the absense of a non added file")
    res = web_client.is_readme_exist(tests_data.new_repo_name, tests_data.branch_name, 'non_exist_fn')
    assert res is False, F"wrongly verified the presence of the README file: {tests_data.branch_name}"


