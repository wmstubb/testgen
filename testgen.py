#!/usr/bin/python

# testgen.py
#
# Given an object descriptor, generate the robot framework test files needed for
# automated testing of the object.
#

import sys
import os
import getopt
#from xml.dom.minidom import parse
import xml.dom.minidom
import xml.dom

import gen_obj_type
import gen_obj_type_obj
import gen_obj_type_plural

def print_usage(exit_code):
    print "testgen.py [-h|-i <inputfile> -o <outputroot>]"
    sys.exit(exit_code)

def process_args(argv):
    processed_args = {}
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=","oroot="])
    except getopt.GetoptError:
            print_usage(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage(0)
        elif opt in ("-i", "--ifile"):
            processed_args["inputfile"] = arg
        elif opt in ("-o", "--oroot"):
            processed_args["outputroot"] = arg
            
    return processed_args

def generate_robot_testfiles(processed_args):
    
    # input file
    input_filename = processed_args["inputfile"]
    # - does it exist? (it has to, we can't conjure up the input data)
    input_exists = os.access(input_filename, os.F_OK)
    if ( input_exists != True ):
        print "input file \"" + input_filename + "\" does not exist"
        exit(2)
    # - can we read from it?
    input_readable = os.access(input_filename,os.R_OK)
    if ( input_readable != True ):
        print "no read access to input file " + input_filename
        exit(2)
    
    # output root directory
    output_root_dir = processed_args["outputroot"]
    # - does it exist?
    output_root_exists = os.access(output_root_dir, os.F_OK)
    if ( output_root_exists != True ): os.makedirs(output_root_dir,0755) # rwxr-xr-x
    # - do we have read access?
    output_root_readable = os.access(output_root_dir,os.R_OK)
    if ( output_root_readable != True ):
        print "no read access to output root directory " + output_root_dir
        exit(2)
    # - do we have write access?
    output_root_writeable = os.access(output_root_dir,os.W_OK)
    if ( output_root_writeable != True ):
        print "no write access to output root directory " + output_root_dir
        exit(2)
    
    # load the input file
    DOMTree = xml.dom.minidom.parse(input_filename)
    
    # the top-level element is the test_object_type
    data_model = DOMTree.documentElement
    data_model_types_set = data_model.getElementsByTagName("prop_data_model_types")
    # there should only be one element with tag name "prop_data_model_types"
    for data_model_types in data_model_types_set:
        generate_robot_testfiles_for_data_model_types(data_model_types,output_root_dir)

def generate_robot_testfiles_for_data_model_types(data_model_types,output_root_dir):
    print "processing " + data_model_types.nodeName
    data_model_type_set = data_model_types.getElementsByTagName("prop_data_model_type")
    for data_model_type in data_model_type_set:
        generate_robot_testfiles_for_data_model_type(data_model_type,output_root_dir)

def generate_robot_testfiles_for_data_model_type(data_model_type,output_root_dir):
    data_type_name = data_model_type.getAttribute("name")
    data_type_aggregate_name = data_model_type.getAttribute("aggregate_name")
    print "processing " + data_model_type.nodeName + " with name " + data_type_name + " and aggregate name " + data_type_aggregate_name
    
    # do a little output root maintenance
    output_dir = os.path.join(output_root_dir,data_type_aggregate_name)
    # - does it exist? (create it if it doesn't)
    output_dir_exists = os.access(output_dir, os.F_OK)
    if ( output_dir_exists != True ): os.makedirs(output_dir,0755) # rwxr-xr-x
    # - can we read from it?
    output_dir_readable = os.access(output_dir,os.R_OK)
    if ( output_dir_readable != True ):
        print "no read access to output root directory " + output_root_dir
        exit(2)
    # - can we write to it?
    output_root_writeable = os.access(output_root_dir,os.W_OK)
    if ( output_root_writeable != True ):
        print "no write access to output root directory " + output_root_dir
        exit(2)
        
    # create the data model type's directory (if needed)
    # generate the data model type's test files
    gen_obj_type_obj.gen_test_code(data_model_type,output_dir)
    gen_obj_type_plural.gen_test_code(data_model_type,output_dir)
    gen_obj_type.gen_test_code(data_model_type,output_dir)

def main(argv):
    processed_args = process_args(argv)
    generate_robot_testfiles(processed_args)

if __name__ == "__main__":
    main(sys.argv[1:])