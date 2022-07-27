import logging
import os
import subprocess
import multiprocessing
from multiprocessing import RLock
import json
from datetime import datetime
from ulid import ULID

from build.rules_functions import *
from build.data_structures import Execution_Data
from build.controllers import Execution_Controller

class RulesEngineTester:
    def __init__(self, test_file_path) -> None:
        self.__log = logging.getLogger("TestRun").getChild("RulesEngineTester")
        self.__subproc_out_txt = ""
        self.__lock = RLock
        self.__test_file_path = test_file_path
        self.__excel_file_path = os.path.join(self.__test_file_path, "temp", "excel_files")

    @property
    def subproc_out_txt(self):
        return self.__subproc_out_txt

    @subproc_out_txt.setter
    def subproc_out_txt(self, name):
        self.__subproc_out_txt = os.path.join(self.__test_file_path, "temp", "diagnostic_files", f"{name}.txt")
    
    @property
    def test_path(self):
        return os.path.join(self.__test_file_path, "postman", "testfromexcel.py")

    def load_json_commands(self, json_file_name=None):
        json_file_name = os.path.join(self.__test_file_path, json_file_name)

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
        
    def execute(self, personal_cmd, filename=None):
        """
        Executes the command sent in a subprocess. 
        These will hit the rulesengine at a specific endpoint. Only accepts 
        Newman commands.

        :param  personal_cmd    ::  list of commands for CLI operation. 

        """     
        if not personal_cmd:
            excel_file_path = os.path.join(self.__excel_file_path, filename)   
            postman_cmd = ['python', f"{self.test_path}", "-r", excel_file_path, "-u", 
                           "https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c"]
        else:
            postman_cmd = ['python', f"{self.test_path}"] + personal_cmd
            for i in range(0, len(personal_cmd)):
                if personal_cmd[i] in ["-g", "-r", "--generate", "--run"]:
                    try:
                        filename = os.path.split(personal_cmd[i+1])[-1]
                        break
                    except IndexError as e:
                        pass
            
        if not filename:
            print("No file or commands given. ")
            return

        self.subproc_out_txt = filename.replace(".xlsx","") 

        with open(self.subproc_out_txt, 'w+') as f:
            f.write(f"Command executed:\n{postman_cmd}\n\n")

        subproc = subprocess.Popen(postman_cmd, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)

        print(f"Subprocess Test for {filename} started.")
        with open(self.subproc_out_txt, 'a', encoding='utf-8') as out_file:
            attempts = 0
            while attempts < 3:
                try:
                    outs, errs = subproc.communicate()
                except subprocess.TimeoutExpired:
                    subproc.kill()
                    attempts = attempts + 1
                    out_file.write(f"Attempt {attempts} complete.")
                    continue
                
                print(f"Attempting to write data for {filename}")
                out_file.write(f"Attempt {attempts} Out:\n")
                outs = outs.decode('utf-8')
                try:
                    outs = "┌"+outs.split("┌")[1]
                except IndexError as e:
                    pass
                out_file.write(outs)
                out_file.write(f"Attempt {attempts} Error:\n")
                out_file.write(errs.decode('utf-8'))

                break

        print(f"Subprocess Test for {filename} complete.")   

        return {self.subproc_out_txt: (outs, errs)}

    def run(self, json_file_name=None):
        """ Performs the test by calling postman/testfromexcel.py. Can be performed on a
            single test or multiple: takes a json with a filename and flags in a string,
            otherwise defaults to using the xlsx files in temp/excel_files.
            
            Defualts:
            Defaults to the xlsx files in temp/excel_files, flag -r. 
            Defaults -u to: 
            https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c

            Be careful when providing -g and -r in the same command. May produce
            unexpceted results- preferably don't. 

            :param tests_to_run    ::  json
                {"test1": "-r,SO_Tests.xlsx,-u,abc", ...}
                Make sure the commands are COMMA seperated 
                and that no file is accessed more than once.            
        """
        
        # excel_file_path = os.path.join("temp", "excel_files")
        tests_to_run = self.load_json_commands(json_file_name)

        all_commands = []
        for key in tests_to_run:
            single_cmd_str = tests_to_run[key].replace(", ", ",")
            test_cmnds_list = single_cmd_str.split(",")
            all_commands.append(test_cmnds_list)
        try:
            if len(all_commands) > 1:
                results = self.multiple_tests_run(all_commands)
            else:
                results = self.execute(all_commands[0])
        except Exception as e:
            self.__log.info(f"An error occured during testing.\n\t {e}")

        self.__log.info("All test complete.")

    def multiple_tests_run(self, all_commands):
        """ Allows parallel execution of newman processes.
            Sends a set of commands to self.execute that calls the newman process.

            :param all_commands ::  list of lists
                [[], [], [] ...] 
        """
        with multiprocessing.Pool(3) as pool:
            try:
                processes = [pool.apply_async(self.execute, args=(personal_cmd,)) for personal_cmd in all_commands]
                results = [proc.get() for proc in processes]
            except Exception as e:
                self.__log.debug(f"Failure during tests. \n\t Error: {e}")
            finally:
                pool.close()
                pool.join()
        
        return results
    
    def write_results(self, results):
        """ Takes a list of dicts of 2D tuple and appends the result the 
            correct txt file- defined by the key.
            
            : param     :: [{filename_path: (outs, errs)}, {...}, ... ]
        """
        for result in results:
            for key in result:  # should only be 1 key
                with open(key, 'a', encoding='utf-8') as out_file:
                    outs = result[key][0].decode('utf-8')
                    errs = result[key][1].decode('utf-8')
                    try:
                        outs = "┌"+outs.split("┌")[1]
                    except IndexError as e:
                        pass
                    out_file.write(outs)
                    out_file.write(errs)

    def run_function_tests(self):
        """ 
        Performs the test by calling functions from the build folder. 
        Runs over all the files available in temp/excel_files      
        """
        self.__log.info("Running function tests. ")
        jsonfilename = self.generate_commands(['-func'])
        self.__log.info("Creating JSONs.  ")
        self.run(jsonfilename)
        self.__test_functions()

    def develop_coverage_report(self):
        self.__log.info("Generating JSONs to simulate payloads. ")
        jsonfilename = self.generate_commands(['-g'])
        self.run(jsonfilename)
        print("Jsons created. Ready to pass json collections to functions.")

    def generate_commands(self, command_list):
        if os.path.exists(self.__excel_file_path):
            excel_file_dir_items = os.listdir(self.__excel_file_path)
            try:
                excel_file_dir_items = self.ignore_in_dir(excel_file_dir_items)
            except IndexError as e:
                print("Folder is empty. ")
            
            all_commands, jsonfilename = self.__generate_json_commands(excel_file_dir_items, 
                                                                   command_list)
        else:
            print(f"Folder {self.__excel_file_path} does not exist or is empty.")
        return jsonfilename

    def ignore_in_dir(self, dir_items):
        return_dir = []
        for i in range(0, len(dir_items)):
            if dir_items[i] == ".git":
                continue
            elif dir_items[i] == "jsons":
                continue
            else:
                return_dir.append(dir_items[i])
        return return_dir

    def __generate_json_commands(self, excel_file_dir_items, command_list):
        """
        If passed -r, will generate commands to run. If -g, will generate commands 
        just to run genreate the excels. If passed -u and -r, will run at a specific
        endpoint. Should be in the order r, g, u.

        :param command_list     :: ['-r', '-u ...'] OR ['-g', '-u ...'] OR
                                   ['-r'] OR ['-g'] OR ['-func']
        """
    
        if '-r' in command_list[0]:
            jsonfilename = "GeneratedJson.json"
        elif '-g' in command_list[0]:
            jsonfilename = "CoverageJson.json"
        elif '-func' in command_list[0]:
            jsonfilename = "FuncNames.json"
        else:
            print("Error, Incorrect Command")
            return

        all_commands = self.__generate_cmd_str(excel_file_dir_items, command_list)

        json_path = os.path.join(self.__test_file_path, jsonfilename)
        with open(json_path, 'w+') as f:
            json.dump(all_commands, f, indent=2)
        print("Commands generated!")

        return all_commands, jsonfilename

    def __generate_cmd_str(self, excel_file_dir_items, command_list):
        """
        Function to generate the command str.
        """   
        all_commands = {}
        i = 0
        if '-func' in command_list[0]:
            for filename in excel_file_dir_items:
                cmd_name = f"cmd {i}"
                file_path = os.path.join(self.__excel_file_path, filename)
                cmd_str = f"-g, {file_path}"
                all_commands[cmd_name] = cmd_str
                i = i + 1 
        else:
            for filename in excel_file_dir_items:
                cmd_name = f"cmd {i}"
                file_path = os.path.join(self.__excel_file_path, filename)
                try:
                    cmd_str = f"{command_list[0]}, {file_path}, {command_list[1]}"
                except IndexError as e:
                    cmd_str = f"{command_list[0]}, {file_path}"
                all_commands[cmd_name] = cmd_str
                i = i + 1 
        return all_commands
    
    def __test_functions(self):
        """
        Tests a specific RulesEngine function, depending on the excel files available.
        Loads all of the function names from FuncNames.json and comapres to the funcs
        in '/build'.

        For each file, it pulls the fuctions and payloads.

        These will run as multiple processes.

        :param  json_file_name    ::  json filename. 
        """

        json_file_path =os.path.join(self.__excel_file_path, "jsons")
        json_file_dir_items =  os.listdir(json_file_path)
        json_file_list = []
        for json_file in range(0, len(json_file_dir_items)):
            if "collection" in json_file_dir_items[json_file]:
                continue
            else:
                json_file_list.append(json_file_dir_items[json_file])
        # multiprocess here
        for json_file_name in json_file_list:
            self.test_a_function(json_file_name)
    
    def test_a_function(self, json_file_name):
        our_keys, payload, all_data = self.get_post_data(json_file_name)
        for test in all_data:
            test_body = test['requestBody']
            
            for i in ["__format_in", "__instructions.modules_to_run[0]", "__instructions.return_path"]:
                try:
                    test_body.pop(i) 
                except IndexError:
                    pass
            # this will work for Amy's Compliance Payload IPL OPL
            to_add = {"orgId": 123,
                        "orgName": "postman--test",
                        "className": "SO_Creation_Test_Trigger",
                        "objectName": "Shipment_Order__c",
                        "debug": True,
                        "formatIn": "flat",
                        "instructions.modulesToRun[0]": "primary_compliance",
                        "instructions.returnPath": ""}
            
            test_body.update(to_add)
            
            mode = 'sync'

            execution_data = Execution_Data()
            execution_data.mode = mode
            execution_data.post_data = test_body
            execution_data.GUID = ULID.from_datetime(datetime.utcnow()) 

            if mode == "sync":
                execution_controller = Execution_Controller(execution_data)
                try:
                    execution_controller.run()
                except Exception as e:
                    print(e)
                else:
                    output_dict = {
                        "__instructions": execution_data.instructions,
                        "out_flat_all": execution_data.working_dict_flat,
                        "out_dev_all": execution_data.working_dict,
                        "out_sf_diff": execution_data.difference_sf,
                    }
        print("HERE")

    def get_post_data(self, json_file_name):
        json_file_path =os.path.join(self.__excel_file_path, "jsons")
        our_keys = {}
        payload = {}
        with open(os.path.join(json_file_path, json_file_name), 'r') as f:
            file_data = json.loads(f.read())
            all_data = file_data
            for test_item_index in range(0, len(file_data)):
                for key in file_data[test_item_index]["requestBody"].keys():
                    if "instruction" in key.lower():
                        our_keys[key] = file_data[test_item_index]["requestBody"][key]
                    elif "debug" in key.lower():
                        our_keys[key] = file_data[test_item_index]["requestBody"][key]
                    elif "format" in key.lower():
                        our_keys[key] = file_data[test_item_index]["requestBody"][key]
                    else:
                        payload[key] = file_data[test_item_index]["requestBody"][key]
        return our_keys, payload, all_data
