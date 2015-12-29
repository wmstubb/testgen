#!/usr/bin/python

# gen_obj_type_plural.py
#
# Given an object descriptor, generate the robot framework test files needed for
# automated testing of the object.
#

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
    
    #properties = data_model_type.getElementsByTagName("property")
#     print "properties:"
#     for property in properties:
#         print property
#     
#     tests = data_model_type.getElementsByTagName("test")
#     print "tests:"
#     for test in tests:
#         print test