import pytest


def test_create_delete_list_repository(api_client, cfg_data, pre_test_activity, logger):
    logger.info(F"\n\n******** Begin a new test execution *****************************************\n")

    logger.info(f'Listing the available repos within project: {cfg_data.proj_name}')
    res = api_client.list_repositories(cfg_data.proj_name)
    assert len(res.result) == 0, F"before creating repo - no repos should be found - wrongly found these/this: {res.msg}"
    logger.info('list is empty as expected - mo repos yet')

    logger.info(f'creating a repo within project: {cfg_data.proj_name}')
    res = api_client.create_repo(cfg_data.repo_name, cfg_data.proj_key)
    assert res.status is True, F"repo failed to create, {res.msg}"
    logger.info(F"repo: {cfg_data.proj_name} was created successfully")

    logger.info(f'Listing the available repos within project: {cfg_data.proj_name} after a creation of a repo')
    res = api_client.list_repositories(cfg_data.proj_name)
    assert res.status is True, F"list repo activity failed, {res.msg}"
    assert ''.join(res.result) == cfg_data.repo_name, (F"expected list of repos per project {cfg_data.proj_name} :"
                                                       F" {cfg_data.repo_name}, actual: {res.result}")
    logger.info(F"repo list contains the {cfg_data.repo_name} as expected")

    logger.info(f'deleting the repo within project: {cfg_data.proj_name}')
    res = api_client.del_repo(cfg_data.repo_name)
    assert res.status is True, F"failed to delete repo, {res.msg}"
    logger.info(F"repo {cfg_data.repo_name} deleted successfully from proj. {cfg_data.proj_name}")

    logger.info(f'Listing the available repos within project: {cfg_data.proj_name} after the deletion of the repo')
    res = api_client.list_repositories(cfg_data.proj_name)
    assert len(res.result) == 0, F"after deleting the repo - no repos should be found - wrongly found these/this: {res.msg}"
    logger.info('list is empty as expected - the repo was deleted')


def test_exercise_scenario(web_client, tests_data, clean_web_workspace, logger):
    logger.info(F"\n\n******** Begin a new test execution *****************************************\n")

    logger.info(F"Create a project in Bitbucket: {tests_data.new_proj_name}")
    res = web_client.create_project(tests_data.new_proj_name, tests_data.new_proj_key)
    assert res is True, F"fail to create a project: {tests_data.new_proj_name}"
    logger.info(F"project {tests_data.new_proj_name} was created successfully")

    logger.info(F"Verify the project's existence: {tests_data.new_proj_name}")
    res = web_client.is_item_exist(tests_data.PROJECTS, tests_data.new_proj_name)
    assert res is True, F"verification failed, project: {tests_data.new_proj_name}"
    logger.info(F"project existence {tests_data.new_proj_name} verified")

    logger.info(F"Navigate to a specific project in Bitbucket: {tests_data.new_proj_name}")
    res = web_client.open_resource(tests_data.PROJECTS, tests_data.new_proj_name)
    assert res is True, F"fail to open a project: {tests_data.new_proj_name}"
    logger.info(F"project: {tests_data.new_proj_name} was opened successfully")

    logger.info(F"Create a new repository: {tests_data.new_repo_name} within project: {tests_data.new_proj_name}")
    res = web_client.create_repo(tests_data.new_proj_name, tests_data.new_repo_name)
    assert res is True, F"fail to create a repo: {tests_data.new_repo_name}"
    logger.info(F"repository: {tests_data.new_repo_name} created successfully within project: {tests_data.new_proj_name}")

    logger.info(F"Verify the existence of repository: {tests_data.new_repo_name}")
    res = web_client.is_item_exist(tests_data.REPOSITORIES, tests_data.new_repo_name)
    assert res is True, F"verification failed, repo: {tests_data.new_repo_name}"
    logger.info(F"repository: {tests_data.new_repo_name} exist")

    logger.info(F"Create a new branch: {tests_data.branch_name} in repository: {tests_data.new_repo_name}")
    res = web_client.create_branch(tests_data.new_repo_name, tests_data.branch_name)
    assert res is True, F"fail to create a branch: {tests_data.branch_name}"
    logger.info(F"branch: {tests_data.branch_name} created successfully in repository: {tests_data.new_repo_name}")

    logger.info(F"Add a README file to branch: {tests_data.branch_name}")
    res = web_client.add_readme(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to add a README file to the branch: {tests_data.branch_name}, filename: {tests_data.filename}"
    logger.info(F"README file was added successfully to branch: {tests_data.branch_name}")

    logger.info(F"Verify the presence of the README file within branch: {tests_data.branch_name}")
    res = web_client.is_readme_exist(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to verify the presence of the README file: {tests_data.branch_name}, filename: {tests_data.filename}"
    logger.info(F"README exist in branch: {tests_data.branch_name}")

    logger.info(F"Merge branch: {tests_data.branch_name} into the main repository branch")
    res = web_client.merge_branch(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, (F"fail merge the branch into the main repository branch: {tests_data.branch_name}, "
                         F"repo name: {tests_data.new_repo_name}")
    logger.info(F"branch: {tests_data.branch_name} merged into the main repository branch")

    logger.info(F"Log out from Bitbucket")
    assert web_client.logout() is True, 'failed to logout'
    logger.info(F"Log out successfully from Bitbucket")


def test_negative_verify_non_exist_file_in_branch(web_client, tests_data, clean_web_workspace, logger):
    logger.info(F"\n\n******** Begin a new test execution *****************************************\n")

    logger.info(F"Create a project in Bitbucket: {tests_data.new_proj_name}")
    res = web_client.create_project(tests_data.new_proj_name, tests_data.new_proj_key)
    assert res is True, F"fail to create a project: {tests_data.new_proj_name}"
    logger.info(F"project {tests_data.new_proj_name} was created successfully")

    logger.info(F"Create a new repository: {tests_data.new_repo_name} within project: {tests_data.new_proj_name}")
    res = web_client.create_repo(tests_data.new_proj_name, tests_data.new_repo_name)
    assert res is True, F"fail to create a repo: {tests_data.new_repo_name}"
    logger.info(
        F"repository: {tests_data.new_repo_name} created successfully within project: {tests_data.new_proj_name}")

    logger.info(F"Create a new branch: {tests_data.branch_name} in repository: {tests_data.new_repo_name}")
    res = web_client.create_branch(tests_data.new_repo_name, tests_data.branch_name)
    assert res is True, F"fail to create a branch: {tests_data.branch_name}"
    logger.info(F"branch: {tests_data.branch_name} created successfully in repository: {tests_data.new_repo_name}")

    logger.info(F"Add a README file to branch: {tests_data.branch_name}")
    res = web_client.add_readme(tests_data.new_repo_name, tests_data.branch_name, tests_data.filename)
    assert res is True, F"fail to add a README file to the branch: {tests_data.branch_name}, filename: {tests_data.filename}"
    logger.info(F"README file was added successfully to branch: {tests_data.branch_name}")

    logger.info(F"Verify the absense of a non added file in branch: {tests_data.branch_name}")
    res = web_client.is_readme_exist(tests_data.new_repo_name, tests_data.branch_name, 'non_exist_fn')
    assert res is False, F"wrongly verified the presence of the README file: {tests_data.branch_name}"
    logger.info(F"the file is absense from branch: {tests_data.branch_name}")
