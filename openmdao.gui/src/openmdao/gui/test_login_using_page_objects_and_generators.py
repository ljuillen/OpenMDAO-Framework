'''
  Run the use case described on
    https://docs.google.com/document/d/16m74ZhD1_TpgmGH_RPTUGthIMCGNsxRhJOpucbDX_4E/edit?hl=en_US
'''
import sys

import time

from multiprocessing import Process

from pageobjects.openmdao_login import LoginPageObject #, ProjectsListPageObject

from openmdao.util.network import get_unused_ip_port

from selenium import webdriver

from distutils.spawn import find_executable

from openmdao.gui.omg import pro

from nose.tools import eq_ as eq
from nose.tools import with_setup

sys.path.append( "." )

port = None
server = None

browsers_to_test = [
    "firefox",
    #"chrome"
    ]

browsers = []
if "firefox" in browsers_to_test :
    firefox = webdriver.Firefox()
    firefox.implicitly_wait(15)
    browsers.append( firefox )
if "chrome" in browsers_to_test :
    chromedriver_path = find_executable( 'chromedriver' )
    #chrome = webdriver.Chrome(executable_path=chromedriver_path)
    chrome = webdriver.Chrome(executable_path='/hx/u/hschilli/bin/chromedriver')
    chrome.implicitly_wait(15)
    browsers.append( chrome )

def setup_server() :
    '''The function gets called once before any of the
    tests are called'''
    
    global port
    global server

    port = get_unused_ip_port()    

    server = Process(target=pro, args=(port,))
    server.start()
        
def teardown_server():
    '''The function gets called once after all of the
    tests are called'''
    
    for browser in browsers:
        browser.close()
    server.terminate()

@with_setup(setup_server, teardown_server)
def test_generator():
    #for browser_name in [ 'firefox', 'chrome' ]:
    #    for _test in [ _test_successful_login, _test_unsuccessful_login, _test_new_project ]:
    #        yield _test, browser_name

    for browser in browsers :
        for _test in [ _test_workflow_basics, ]:
            yield _test, browser

def _test_successful_login(browser):
    successful_login(browser)

def successful_login(browser):
    login_page = LoginPageObject(browser, port)
    login_page.go_to()
    eq( "Login", login_page.page_title )
    projects_page = login_page.login_successfully("herb", "herb" )
    eq( "Projects", projects_page.page_title )
    eq( "http://localhost:%d/" % port, projects_page.page_url )
    assert projects_page.is_element_present( *projects_page.locators["logout"] )
    login_page_again = projects_page.logout()
    eq( "Login", login_page_again.page_title )
    
def _test_unsuccessful_login(browser):
    unsuccessful_login(browser)

def unsuccessful_login(browser):
    login_page = LoginPageObject(browser, port)
    login_page.go_to()
    eq( "Login", login_page.page_title )
    new_login_page = login_page.login_unsuccessfully("herb", "notherb" )
    eq( "Login", new_login_page.page_title )

def _test_new_project(browser):
    new_project(browser)

def new_project(browser):
    login_page = LoginPageObject(browser, port)
    login_page.go_to()
    eq( "Login", login_page.page_title )

    projects_page = login_page.login_successfully("herb", "herb" )
    eq( "Projects", projects_page.page_title )
    
    new_project_page = projects_page.new_project()
    assert new_project_page.page_title.startswith( "New Project" )
    
    new_project_name = new_project_page.get_random_project_name()
    new_project_description = "just a project generated by a test script"
    new_project_version = "initial version"
    new_project_shared = True
    project_info_page = new_project_page.create_project(
        new_project_name,
        new_project_description, 
        new_project_version, 
        new_project_shared
        )
    
    time.sleep(2)

    project_info_page.assert_on_correct_page()
    
    eq( new_project_name, project_info_page.page_title )

    # go back to projects page to see if it is on the list
    projects_page_again = project_info_page.go_to_projects_page()
    assert projects_page_again.is_project_with_this_name_on_list( new_project_name )
    
    login_page_again = projects_page_again.logout()
    eq( "Login", login_page_again.page_title )
    
def _test_workflow_basics(browser):
    workflow_basics(browser)

def workflow_basics(browser):
    login_page = LoginPageObject(browser, port)
    login_page.go_to()
    eq( "Login", login_page.page_title )

    projects_page = login_page.login_successfully("herb", "herb" )
    eq( "Projects", projects_page.page_title )
    
    new_project_page = projects_page.new_project()
    assert new_project_page.page_title.startswith( "New Project" )
    
    new_project_name = new_project_page.get_random_project_name()
    new_project_description = "just a project generated by a test script"
    new_project_version = "initial version"
    new_project_shared = True
    project_info_page = new_project_page.create_project(
        new_project_name,
        new_project_description, 
        new_project_version, 
        new_project_shared
        )

    project_info_page.assert_on_correct_page()
    eq( new_project_name, project_info_page.page_title )

    workspace_page = project_info_page.load_project_into_workspace()
    workspace_page.assert_on_correct_page()

    # View the Code Editor
    workspace_page.view_code_editor()

    time.sleep(4)

    # View the Workflow Pane
    workspace_page.view_workflow()

    time.sleep(4)

    # Add paraboloid file
    import openmdao.examples.simple.paraboloid
    file_path = openmdao.examples.simple.paraboloid.__file__
    if file_path.endswith( ".pyc" ):
        file_path = file_path[ :-1 ]
    workspace_page.add_file( file_path )

    # Add optimization_unconstrained file
    import openmdao.examples.simple.optimization_unconstrained
    file_path = openmdao.examples.simple.optimization_unconstrained.__file__
    if file_path.endswith( ".pyc" ):
        file_path = file_path[ :-1 ]
    workspace_page.add_file( file_path )

    # View Refresh
    workspace_page.view_refresh()

    # Check to make sure the files were added
    file_names = workspace_page.get_files()
    expected_file_names = [
        "paraboloid.py",
        "optimization_unconstrained.py",
        ]
    if not sorted( file_names ) == sorted( expected_file_names ):
        raise self.failureException(
            "Expected file names, '%s', should match existing file names, '%s'" \
            % ( expected_file_names, file_names))
    
    time.sleep(4) # Wait for the View menu to roll up

    #import pdb; pdb.set_trace()
    
    # Import * from paraboloid
    workspace_page.import_from_file( "paraboloid.py" )

    time.sleep(2)

    # Import * from optimization_unconstrained
    workspace_page.import_from_file( "optimization_unconstrained.py" )

    # Select Libraries Tab
    workspace_page.libraries_tab()

    # Go into working section
    workspace_page.working_section()

    # View structure
    workspace_page.view_structure()

    # Make sure there is only one dataflow component
    eq( workspace_page.get_number_of_dataflow_components(), 1 )

    # Drag element into workspace
    paraboloid_name = 'parab'
    workspace_page.add_library_item_to_structure( 'Paraboloid', paraboloid_name )

    #import pdb; pdb.set_trace()
    
    # Now there should be two
    eq( workspace_page.get_number_of_dataflow_components(), 2 )

    # Make sure the item added is there with the name we gave it
    component_names = workspace_page.get_dataflow_component_names()
    if paraboloid_name not in component_names :
        raise self.failureException(
            "Expected component name, '%s', to be in list of existing component names, '%s'" \
            % ( paraboloid_name, component_names))

    workspace_page.save_project()
    projects_page_again = workspace_page.close_workspace()

    # Now try to re-open that project to see if items are still there
    project_info_page = projects_page_again.open_project( new_project_name )

    # Make sure all the project meta data was saved correctly
    eq( project_info_page.project_name, new_project_name )
    eq( project_info_page.description, new_project_description )
    eq( project_info_page.version, new_project_version )
    eq( project_info_page.shared, new_project_shared )

    workspace_page = project_info_page.load_project_into_workspace()

    time.sleep(2)

    # Check to see that the added files are still there
    workspace_page.files_tab()
    file_names = workspace_page.get_files()
    expected_file_names = [
        "paraboloid.py",
        "optimization_unconstrained.py",
        ]
    if not sorted( file_names ) == sorted( expected_file_names ):
        raise self.failureException(
            "Expected file names, '%s', should match existing file names, '%s'" \
            % ( expected_file_names, file_names))

    projects_page_again = workspace_page.close_workspace()

    login_page_again = projects_page_again.logout()

    time.sleep(2)
    login_page_again.assert_on_correct_page()
    
    
