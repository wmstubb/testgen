#!/usr/bin/python

# gen_obj_type.py
#
# Given a DOM node of type prop_data_model_type, this module updates (or
# creates if needed) a robot framework test file containing the following
# keywords for each test:
#
#   keyword: <test>
#   keyword: Verify <test> Results
#   keyword: Verify <test> Results via UI
#   keyword: Verify <test> Results via DB
#
# The test file should contain the boilerplate for each test as defined above
# and if there already exists a target file, this module should integrate the
# non-boilerplate test code into the new file.
#
# Upon completion, the following will exist:
#
#   <output_root_dir>/<prop_data_model_type>/<prop_data_model_type>.txt
#   <output_root_dir>/<prop_data_model_type>/<prop_data_model_type>_orig.txt
#
# <prop_data_model_type>_orig.txt is the copy of <prop_data_model_type>.txt

import sys
import os
import xml.dom
    
def gen_test_code(data_model_type,output_dir):
    
    # get the test object type's name (e.g. "railcar")
    if data_model_type.hasAttribute("name"):
        data_model_type_name = data_model_type.getAttribute("name")
    else:
        print "data_model_type needs a name attribute"
        sys.exit(2)
        
    # get the test object type's aggregate name (e.g. "railcars")
    if data_model_type.hasAttribute("aggregate_name"):
        data_model_type_aggregate_name = data_model_type.getAttribute("aggregate_name")
    else:
        print "data_model_type needs an aggregate_name attribute"
        sys.exit(2)
        
    output_filename = data_model_type_name + "_tmp.txt"
    output_file_fdn = os.path.join(output_dir,output_filename)
    ofile = open(output_file_fdn,"w")
    
    # generate the test file front matter
    # - this begins the file
    write_header(ofile,data_model_type_name)
    
    # generate the test file's session management keywords
    write_session_keyword_header_for_tests(ofile)
    tests_set = data_model_type.getElementsByTagName("tests")
    for tests in tests_set:
        write_session_keywords_for_tests(ofile,tests)
    write_session_keyword_trailer_for_tests(ofile)
    
    # generate the test file's test execution keywords
    write_test_keywords_header(ofile)
    for tests in tests_set:
        if tests.hasAttribute("test_object"):
            test_object = tests.getAttribute("test_object")
        else:
            print "tests needs a test_object attribute"
            sys.exit(2)
        write_test_keywords(ofile,tests,data_model_type_name,test_object)
    write_test_keywords_trailer(ofile)
    
    # generate the test file's utility keywords
    write_utility_keywords_header(ofile)
    write_utility_keywords(ofile,data_model_type_name,test_object)
    write_utility_keywords_trailer(ofile)
    
    # generate the test file back matter
    # - this ends the file
    write_trailer(ofile,data_model_type_name)

def write_session_keywords_for_tests(ofile,tests):
    test_set = tests.getElementsByTagName("test")
    for test in test_set:
        write_session_keywords_for_test(ofile,test)

def write_test_keywords(ofile,tests,data_model_type_name,test_object):
    test_set = tests.getElementsByTagName("test")
    for test in test_set:
        write_test_keyword(ofile,test,data_model_type_name,test_object)
    
##########################################
# the actual writing functions are below #
##########################################

#
# test file beginning and ending text
#

# - the file's beginning
def write_header(ofile,test_object_type):
    ofile.write("*** Settings ***\n")
    ofile.write("Documentation     A resource file providing " + test_object_type + " keywords.\n")
    ofile.write(
"""...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
Library           Selenium2Library
Library           DatabaseLibrary
Library           String

*** Variables ***

*** Keywords ***

""")

# - the file's ending
def write_trailer(ofile,test_object_type):
    pass # no trailing information at this time

#
# test file's session management keywords
#

# - session management header
def write_session_keyword_header_for_tests(ofile):
    ofile.write(
"""##########################
# session keywords begin #
##########################

""" )

# - session management trailer
def write_session_keyword_trailer_for_tests(ofile):
    ofile.write(
"""########################
# session keywords end #
########################

""" )

# - session management keywords (invoked once per test)
def write_session_keywords_for_test(ofile,test):
    # extract the attributes
    # - test name
    if test.hasAttribute("name"):
        test_name = test.getAttribute("name")
    else:
        print "test needs a name attribute"
        sys.exit(2)
    # - default CIG user role (to perform this test)
    if test.hasAttribute("default_cig_user_role"):
        default_cig_user_role = test.getAttribute("default_cig_user_role")
    else:
        print "test needs a default_cig_user_role attribute"
        sys.exit(2)
    # - default FML user role (to perform this test)
    if test.hasAttribute("default_fml_user_role"):
        default_fml_user_role = test.getAttribute("default_fml_user_role")
    else:
        print "test needs a default_fml_user_role attribute"
        sys.exit(2)
        
    # now add test keywords for the test/roles values
    ofile.write("Default User to " + test_name + "\n")
    ofile.write("    [Documentation]  *Default User to " + test_name + "*\n")
    ofile.write("    ...              Returns the default user to use when performing this test.\n")
    if ( default_cig_user_role == default_fml_user_role ):
        # the user choice is not dependent upon the runtime environment - it's the same either way
        ofile.write("    ${user} =  Users.Get User By Account Type  " + default_cig_user_role + "\n")
    else:
        ofile.write("    ${cig_user} =  Users.Get User By Account Type  " + default_cig_user_role + "\n")
        ofile.write("    ${fml_user} =  Users.Get User By Account Type  " + default_fml_user_role + "\n")
        ofile.write("    ${running_in_cig} =  Resources.Running In CIG Environment\n")
        ofile.write("    ${user} =  Set Variable If  '${running_in_cig}' == 'True'  ${cig_user}  ${fml_user}\n")
    ofile.write("    [Return]  ${user}\n\n")
    
    ofile.write("Login To " + test_name + "\n")
    if ( default_cig_user_role == default_fml_user_role ):
        # the user choice is not dependent upon the runtime environment - it's the same either way
        ofile.write("    Resources." + default_cig_user_role + " is Logged In to Terminal\n\n")
    else:
        ofile.write("    ${running_in_cig} =  Resources.Running In CIG Environment\n")
        ofile.write("    Run Keyword If  '${running_in_cig}' == 'True'  Resources." + default_cig_user_role + " is Logged In to Terminal\n")
        ofile.write("    Run Keyword If  '${running_in_cig}' != 'True'  Resources." + default_fml_user_role + " is Logged In to Terminal\n\n")

#
# test file's test keywords
#

# - test keyword section header
def write_test_keywords_header(ofile):
    ofile.write(
"""#######################
# test keywords begin #
#######################

""" )

# - test keyword section trailer
def write_test_keywords_trailer(ofile):
    ofile.write(
"""#####################
# test keywords end #
#####################

""" )

# - test
def write_test_keyword(ofile,test,data_model_type_name,test_object):
    # extract the attributes
    # - test name
    if test.hasAttribute("name"):
        test_name = test.getAttribute("name")
    else:
        print "test needs a name attribute"
        sys.exit(2)
    # - banner message
    if test.hasAttribute("banner_msg"):
        test_banner_msg = test.getAttribute("banner_msg")
    else:
        print "test needs a name attribute"
        sys.exit(2)
        
    # now add test keywords for the test/roles values
    # - begin with the step with executes the test
    ofile.write("# begin generated code\n\n")
    ofile.write(test_name + "\n")
    ofile.write("    [Documentation]  *Test the " + test_name + " function for this application object type.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("    ${banner} =  Boxed String  " + test_banner_msg + "\n")
    ofile.write("    Log to Console  \\n${banner}\n")
    ofile.write("    Model.Print  " + test_object + "\n")
    ofile.write("\n")
    ofile.write("# end generated code\n")
    ofile.write("\n")
    # - next comes the validation
    verify_test_keyword_localname = "Verify " + test_name
    verify_test_keyword_fullname = data_model_type_name + "." + verify_test_keyword_localname
    verify_test_via_ui_keyword_localname = verify_test_keyword_localname + " Via UI"
    verify_test_via_ui_keyword_fullname = data_model_type_name + "." + verify_test_via_ui_keyword_localname
    verify_test_via_db_keyword_localname = verify_test_keyword_localname + " Via DB"
    verify_test_via_db_keyword_fullname = data_model_type_name + "." + verify_test_via_db_keyword_localname
    verify_via_ui_keyword_localname = "Verify Via UI"
    verify_via_ui_keyword_fullname = data_model_type_name + "." + verify_via_ui_keyword_localname
    verify_via_db_keyword_localname = "Verify Via DB"
    verify_via_db_keyword_fullname = data_model_type_name + "." + verify_via_db_keyword_localname
    ofile.write("# begin generated code\n")
    ofile.write("\n")
    ofile.write("    # now check our work...\n")
    ofile.write("\n")
    ofile.write("    Run Keyword If  '${test_mode}' == 'white_box'  " + verify_test_keyword_fullname + "  " + test_object + "\n")
    ofile.write("\n")
    ofile.write(verify_test_keyword_localname + "\n")
    ofile.write("    [Documentation]  *Verify the result of the " + test_name + " test.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("    ${banner} =  Boxed String  verifying test results\n")
    ofile.write("    Log to Console  \\n${banner}\n")
    ofile.write("    Model.Print  " + test_object + "\n")
    ofile.write("\n")
    ofile.write("    " + verify_test_via_ui_keyword_fullname + "  " + test_object + "\n")
    ofile.write("    " + verify_test_via_db_keyword_fullname + "  " + test_object + "\n")
    ofile.write("\n")
    ofile.write(verify_test_via_ui_keyword_localname + "\n")
    ofile.write("    [Documentation]  *Verify the result of the " + test_name + " test using the UI.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("    " + verify_via_ui_keyword_fullname + "  " + test_object + "\n")
    ofile.write("\n")
    ofile.write(verify_test_via_db_keyword_localname + "\n")
    ofile.write("    [Documentation]  *Verify the result of the " + test_name + " test using the DB.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("    " + verify_via_db_keyword_fullname + "  " + test_object + "\n")
    ofile.write("\n")
    
    

#
# test file's utility keywords
#

# - utility keyword section header
def write_utility_keywords_header(ofile):
    ofile.write(
"""##########################
# utility keywords begin #
##########################

""" )

# - utility keyword section trailer
def write_utility_keywords_trailer(ofile):
    ofile.write(
"""########################
# utility keywords end #
########################

""" )

# - test
def write_utility_keywords(ofile,data_model_type_name,test_object):
    # utility keywords are general in nature (not test-specific)

    verify_via_ui_keyword_localname = "Verify Via UI"
    verify_via_ui_keyword_fullname = data_model_type_name + "." + verify_via_ui_keyword_localname
    verify_via_db_keyword_localname = "Verify Via DB"
    verify_via_db_keyword_fullname = data_model_type_name + "." + verify_via_db_keyword_localname
        
    # now add test keywords for the test/roles values
    # - begin with the step with executes the test
    ofile.write("# begin generated code\n\n")
    ofile.write(verify_via_ui_keyword_localname + "\n")
    ofile.write("    [Documentation]  *Verify that our model still reconciles with the app using the UI.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("# end generated code\n\n")
    ofile.write("# begin generated code\n\n")
    ofile.write(verify_via_db_keyword_localname + "\n")
    ofile.write("    [Documentation]  *Verify that our model still reconciles with the app using the DB.*\n")
    ofile.write("    [Arguments]      " + test_object + "\n")
    ofile.write("\n")
    ofile.write("# end generated code\n\n")