import os
import json
import keyring
import shutil

__PATHS = {'temp_folder': os.path.join(os.getcwd(), "temp"),
            'diagnostic_files': os.path.join(os.getcwd(), "temp", "diagnostic_files"),
            'excel_files': os.path.join(os.getcwd(), "temp", "excel_files"),
            'jsons': os.path.join(os.getcwd(), "temp", "excel_files", "jsons")}

def get_gitlab_token():
    with open(os.path.abspath('./creds_reference.json'), 'r') as f:
        __CREDENTIALS__ = json.load(f)
        __CREDENTIALS__ = __CREDENTIALS__['GitLabUser-FlaskToken']
        
        token = keyring.get_password(__CREDENTIALS__['service_name'], __CREDENTIALS__['username'])
    
    return token

def rename_folder(repo_folder_name):
    current_path = os.path.join()
    repo_path = os.path.join(current_path, repo_folder_name)
    _path = os.path.join(current_path, 'excel_files')
    cmds_args = f"mv {repo_path} {current_path}"

def delete_old_data(excel_file_path, json_folder_path):
    #### THIS FUNCTION IS STRUGGLING WITH .git ACCESS
    try:
        # os.rmdir(excel_file_path)
        shutil.rmtree(excel_file_path)
    except Exception as e:
        print(e)

def remake_folder(folder_path):
    if not os.path.exists(folder_path):
            os.mkdir(folder_path)

def update_files():
    """
    Function that updates the files in the /temp/excel_files 
    folder. Pulls the files from the 'RulesEngineExcels' git 
    lab repo at: https://git.tecexlabs.dev/NiravS/rulesengineexcels

    :param  ::  excel_file_path
        takes the path to the excel folder -> should be
        '.../temp/excel_files'
    """

    delete_old_data(__PATHS['excel_files'], __PATHS['jsons'])

    remake_folder(__PATHS['excel_files'])

    repo_folder_name = 'rulesengineexcels'
    token = get_gitlab_token()
    cmd_args = f"git clone https://oauth2:{token}@git.tecexlabs.dev/NiravS/{repo_folder_name}.git {__PATHS['excel_files']}"
    os.system(cmd_args)
    try:
        os.remove(os.path.join(__PATHS['excel_files'], 'README.md'))
    except FileNotFoundError:
        pass

    remake_folder(__PATHS['jsons'])
    
    