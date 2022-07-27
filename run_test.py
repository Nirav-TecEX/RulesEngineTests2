"""
run_test.py
=================
``run_test`` is a command line tool which either runns tests defined in excel spreadsheets, or generates a coverage report.

This is a commandline tool, please invoke with the following command line options

General usage:

``run_test <arg> ``

This tool only takes one argument.
    1. 'XXXX.json'
    2. 'coverage-report'

If a json file is specified, it will load ths commands from it. The specified excel testsheets should be in /temp/excel_files.
Alternatively, run the `` generate_jsons.bat `` file to create all of the RUN-type commands for all the files in 
/temp/excel_files. 
    -> See the postman/testfromexcel.py file for more instructions on its flags.

If command 2. is specified, it is expected that all of the excel testsheets are in the temp/excel_files folder. 
"""

import json
import logging
from logging.config import dictConfig
import time
import os
import sys

from test.testrun.testengine import RulesEngineTester
from test.git_api.misc import update_files

__TEST_PATH = os.path.join(os.getcwd(), 'test')
__PATHS = {'temp_folder': os.path.join(__TEST_PATH, "temp"),
            'diagnostic_files': os.path.join(__TEST_PATH, "temp", "diagnostic_files"),
            'excel_files': os.path.join(__TEST_PATH, "temp", "excel_files"),
            'jsons': os.path.join(__TEST_PATH, "temp", "excel_files", "jsons")}

##---------------------------------------------------------------------------------------
def make_folders():
    for key in __PATHS.keys():
        if not os.path.exists(__PATHS[key]):
            os.mkdir(__PATHS[key])
##---------------------------------------------------------------------------------------

##---------------------------------------------------------------------------------------
def load_json_commands(json_file_name=None):
    if json_file_name:
        try:
            with open(json_file_name) as f:
                json_commands = json.load(f)
        except FileNotFoundError:
            print("""
                    SELECTED file does not exist. Please use add a useable
                    filename as an arg. """)
    else:
        try:
            with open(json_file_name) as f:
                json_commands = json.load(f)
        except FileNotFoundError:
            print(f"""
                DEFAULT file ({json_file_name})does not exist. Please use add a 
                useable filename as an arg. """)

    return json_commands
##---------------------------------------------------------------------------------------

##---------------------------------------------------------------------------------------
def filter_args(arg):
    filtered_args = {"test_functions": False,
                     "coverage_report": False}
    try:
        if "funcs" in arg: 
            filtered_args["test_functions"] = True
        elif 'coverage-report' in arg:
            filtered_args["coverage_report"] = True

    except IndexError:
        print("\nNo argument given. Will attempt to run the DEFAULT process.\n")
    
    return filtered_args
##---------------------------------------------------------------------------------------

def test_main(argv):
    with open(os.path.join(__TEST_PATH, "logging_config.json")) as f:
        log_config = json.load(f)
    dictConfig(log_config)

    __log = logging.getLogger("TestRun")

    __log.info("Checking/Creating folder directory... ")
    make_folders()

    filtered_args = filter_args(argv)
    
    test_RE = RulesEngineTester(__TEST_PATH)

    if filtered_args["test_functions"]:
        __log.info(f"Running tests from excel spread sheets. ")

        try:
            test_RE.run_function_tests()
            print("Tests Complete... \n Shutting down...")
        except Exception as e:
            raise "Unable to instantiate the RulesEngineTester class."

        # except Exception as e:
        #     __log.info(f"Error during process. Shutting down ...")
    
    elif filtered_args["coverage_report"]:
        __log.info(f"Generating coverage report. ")
        try:
            test_RE.develop_coverage_report()
        except Exception as e:
            print(f"Error when developing coverage report. Error {e}")
    time.sleep(5)

if __name__ == "__main__":
    with open("logging_config.json") as f:
        log_config = json.load(f)
    dictConfig(log_config)

    __log = logging.getLogger("TestRun")

    __log.info("Checking/Creating folder directory... ")
    make_folders()

    filtered_args = filter_args(sys.argv[1:])
    json_file_name = filtered_args["json_file_name"]
    
    test_RE = RulesEngineTester(__PATHS['excel_files'])

    if not filtered_args["coverage_report"]:
        __log.info(f"Running tests from excel spread sheets. ")

        if not json_file_name:
            json_file_name = "GeneratedJson.json"
    
        __log.info(f"Using file {json_file_name}")
        
        try:
            json_commands = load_json_commands(json_file_name)

            try:
                test_RE.run(tests_to_run=json_commands)
                print("Tests Complete... \n Shutting down...")
            except Exception as e:
                raise "Unable to instantiate the RulesEngineTester class."

        except Exception as e:
            __log.info(f"Error during process. Shutting down ...")
    
    elif filtered_args["coverage_report"]:
        __log.info(f"Generating coverage report. ")
        try:
            test_RE.develop_coverage_report()
        except Exception as e:
            print(f"Error when developing coverage report. Error {e}")

    time.sleep(5)
