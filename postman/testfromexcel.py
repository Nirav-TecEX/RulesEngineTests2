#!/usr/bin/env python3
"""
testfromexcel.py
=================
``testfromexcel`` command line tool to generate various test files and collections from Excel test sheets

This is a commandline tool, please invoke with the following command line options

General usage:

``testfromexcel <--generate>|<--run> <(filename.xlsx)|(filename.json)|(filename_collection.json)> ``

If you specify "generate" and you provide an xlsx file, it will generate the filename.json and the filename_collection.json.
Any existing files will be overwritten.

If you specify "generate" and you provide a .json file, it will generate the _collection.json file, and overwrite any existing file

If you specify "generate" and you provide a _collection.json file, then there's nothing to do.

If you specify "run" then as for above, and it will execute the tests using a separate installation of Newman.

Newman has to installed separately, see https://support.postman.com/hc/en-us/articles/115003703325-How-to-install-Newman
"""

import sys
import os
import getopt
import re
import json

from excelToJson import *
from collectionGeneration import *

global cmd_opts

##---------------------------------------------------------------------------------
def generate_test_from_excel(test_filename :str, excel_filename :str, force_url: str, debug_1=False):
    print("Processing: ", os.path.abspath(excel_filename))
    test_dict = read_excel(excel_filename, force_url)
    if len(test_dict) == 0:
        print('No sheets were processed. Nothing more to do.')
        sys.exit(2)
    generate_test(test_dict, test_filename)
    print("Generated: ", os.path.abspath(test_filename))
    print()
    pass
##---------------------------------------------------------------------------------

##---------------------------------------------------------------------------------
def generate_collection_from_test(collection_filename :str, test_filename :str, force_url: str, debug_1=False):
    print("Processing: ", os.path.abspath(test_filename))

    jsonRequest = populateCollection(test_filename)
    createCollection(jsonRequest, collection_filename)
    
    print("Generated: ", os.path.abspath(collection_filename))
    print()
    pass
##---------------------------------------------------------------------------------

##---------------------------------------------------------------------------------
def run_collection(collection_filename :str, debug_1=False):
    collection_filename = os.path.split(collection_filename)
    collection_file_path = os.path.join(collection_filename[0], 'jsons', collection_filename[-1])
    print("Processing: ", collection_file_path)
    os.system(' newman run  "' + collection_file_path +'"')
    print()
    pass
##---------------------------------------------------------------------------------


##---------------------------------------------------------------------------------
def main(argv):
    global cmd_opts

    print(
"""
testfromexcel usage:

-g or --generate <filename>
   If you provide a .xlsx file, it will generate .json and _collection.json files
   If you provide a .json file it will generate a _collection.json file

-r or --run <filename>
   As above, but after generating the files it will run newman

-u or --url <endpoint url>
   Generate test files that use this URL. This will override the URL specified in the XLSX file

""")

    try:
        opts, args = getopt.getopt(argv, "g:r:u:d", ["generate=", "run=","url=", "debug"])
    except getopt.GetoptError:
        print('testfromexcel parameter error. Please read the documentation.')
        sys.exit(1)

    cmd_opts = {
        "excel_file" : "",
        "test_file" : "",
        "collection_file" : "",
        "force_url" : "",
        "run_at_end" : False,
        "debug_1" : False
    }

    command = ""
    for opt, arg in opts:
        if opt in ["-d", "--debug"]:
            cmd_opts["debug_1"] = True
        elif opt in ["-u", "--url"]:
            cmd_opts["force_url"] = arg
        elif opt in ["-g", "-r", "--generate", "--run"]:
            if (opt in ["-r", "--run"]):
                cmd_opts["run_at_end"] = True

            filename_provided = arg
            if re.search(r'.xlsx?$', filename_provided, re.IGNORECASE):
                cmd_opts["excel_file"] = filename_provided
                cmd_opts["test_file"] = re.sub(r'\.xlsx?$', '.json', filename_provided, re.IGNORECASE)
                cmd_opts["collection_file"] = re.sub(r'\.xlsx?$', '_collection.json', filename_provided, re.IGNORECASE)
            elif  re.search(r'(?<!_collection)\.json$', filename_provided, re.IGNORECASE):
                cmd_opts["test_file"] = filename_provided
                cmd_opts["collection_file"] = re.sub(r'\.json?$', '_collection.json', filename_provided, re.IGNORECASE)
            elif re.search(r'_collection\.json$', filename_provided, re.IGNORECASE):
                cmd_opts["collection_file"] = filename_provided
            else:
                print('testfromexcel parameter error: invalid filename provided.')
                sys.exit(1)

    if cmd_opts["excel_file"]:      cmd_opts["excel_file"] = os.path.normpath(cmd_opts["excel_file"])
    if cmd_opts["test_file"]:       cmd_opts["test_file"] = os.path.normpath(cmd_opts["test_file"])
    if cmd_opts["collection_file"]: cmd_opts["collection_file"] = os.path.normpath(cmd_opts["collection_file"])

    print("Will proceed with the following options : \n", json.dumps(cmd_opts, indent=2), "\n")
    
    if cmd_opts["excel_file"] and cmd_opts["test_file"]:
        generate_test_from_excel(
            test_filename=cmd_opts["test_file"], 
            excel_filename=cmd_opts["excel_file"], 
            force_url=cmd_opts["force_url"],
            debug_1=cmd_opts["debug_1"])

    if cmd_opts["test_file"] and cmd_opts["collection_file"]:
        generate_collection_from_test(
            collection_filename=cmd_opts["collection_file"],
            test_filename=cmd_opts["test_file"], 
            force_url=cmd_opts["force_url"],
            debug_1=cmd_opts["debug_1"])

    if cmd_opts["collection_file"] and cmd_opts["run_at_end"]:
        run_collection(collection_filename=cmd_opts["collection_file"], debug_1=cmd_opts["debug_1"])

##---------------------------------------------------------------------------------


## MAIN ###########################################################################
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8',line_buffering=True)

    main(sys.argv[1:])

#####################################################################################
