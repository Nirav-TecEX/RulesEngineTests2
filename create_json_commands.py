"""

This file is used to quickly generate the json commands
from the excel files in */temp/excel_files/ .

"""

import os
import json
from time import sleep

def generate_commands(_path, excel_file_dir_items):
    all_commands = {}
    i = 0
    for filename in excel_file_dir_items:
        cmd_name = f"cmd {i}"
        file_path = os.path.join(_path, filename)
        cmd_str = f"-r, {file_path}, -u, https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c"
        all_commands[cmd_name] = cmd_str
        i = i + 1 
    return all_commands

if __name__ == "__main__":
    print("Attempting to create jsons...")
    sleep(0.5)
    _base_path = os.path.join(os.getcwd()) 
    _path = os.path.join(_base_path, "temp", "excel_files")
    if os.path.exists(_path):
        excel_file_dir_items = os.listdir(_path)
        try:
            if excel_file_dir_items[0] == '.git':
                excel_file_dir_items.pop(0)
            if excel_file_dir_items[0] == 'jsons':
                excel_file_dir_items.pop(0)
        except IndexError as e:
            print("Folder is empty. ")
        
        all_commands = generate_commands(_path, excel_file_dir_items)

        json_path = os.path.join(_base_path, "GeneratedJson.json")
        with open(json_path, 'w+') as f:
            # json_obj = json.dumps(all_commands)
            json.dump(all_commands, f, indent=2)
        print("Done!")
    else:
        print(f"Folder {_path} does not exist or is empty.")

    sleep(3)
