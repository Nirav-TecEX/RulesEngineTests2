import os
import keyring
import gitlab
import json
import pandas as pd
import base64
import openpyxl

def update_rules_eng_jsons(request_details):
    with open(os.path.abspath('./creds_reference.json'), 'r') as f:
        __CREDENTIALS__ = json.load(f)
        __CREDENTIALS__ = __CREDENTIALS__['GitLabUser-FlaskToken']
    
    token = keyring.get_password(__CREDENTIALS__['service_name'], __CREDENTIALS__['username'])
    gl = gitlab.Gitlab(url='https://git.tecexlabs.dev', private_token=token)
    # x = gl.http_get("https://git.tecexlabs.dev/NiravS/v4/api/projects/18/repository/files")

    projects = gl.projects.list(all=True)
    for project in projects:
        # print("Proj: ", project.name)
        if project.name.lower() != "rulesengineexcels":
            continue
        else:
            break
    pd.e
    project_files = project.repository_tree()
    for file in project_files:
        if file['name'] != 'README.md':
            print(file['name'])
            file_ = project.files.get(file['name'], 'main')
            data = base64.b64decode(file_.content)
            excel_file = pd.ExcelFile(data, engine="openpyxl")
        #     excel_file = opxyl.load_workbook(excel_doc)

        # try:
        #     excel_file.save(path)
            pd_data1 = pd.read_excel(file_.decode())
            break
