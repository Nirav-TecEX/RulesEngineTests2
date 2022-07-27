import json
import os
from tests import *
from excelToJson import *
import argparse
import os.path
from datetime import datetime
import subprocess
import re
#import openpyxl


def createCollection(jsonRequest, collection_filename):
    #Below is the basedata that we do not want to change, as such, it will stay consistent
    basedata = {
        "info" : {
        "_postman_id": "a4533968-075a-4cdc-8ab0-d1201bcad6b2",
		"name": "Testing from Python : "+ datetime.now().strftime("%H:%M:%S - %b %d %Y") +"",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item":jsonRequest,
         "event": [
    {
      "listen": "prerequest",
      "script": {
        "type": "text/javascript",
        "exec": [
          ""
        ]
      }
    },
    {
      "listen": "test",
      "script": {
        "type": "text/javascript",
        "exec": [
          ""
        ]
      }
    }
  ],
  "variable": [
    {
      "key": "stagingResponse",
      "value": "",
      "type": "string"
    }
  ]

        }

    

#Writing the base data to a Json file, which can then either be used by Newman, or imported into Postman
    json_string = json.dumps(basedata, indent = 4)
    collection_filename = os.path.split(collection_filename)
    collection_file_path = os.path.join(collection_filename[0], 'jsons', collection_filename[-1])
    with open(collection_file_path, 'w') as outfile:
        outfile.write(json_string)
    #print(json_string)

    return basedata

def createTestString(request, teststring, fieldPrefix=""):
        if('valueTest' in request.keys()):
            teststring += str(addValueTest(request["valueTest"], fieldPrefix))

        if('fieldCheckTest' in request.keys()):
            teststring += str(addFieldCheckTest(request["fieldCheckTest"], fieldPrefix))

        if('valueContainTest' in request.keys()):
            teststring += str(addContainTest(request["valueContainTest"], fieldPrefix))
        
        if('compareUrl' in request.keys()):
        
            teststring += str(endpointCompareTestString())
       
        if('numCompare' in request.keys()):
            teststring += str(addNumCompareTest(request["numCompare"], fieldPrefix))

        if('expectedResponse' in request.keys()):
            teststring += str(addExpectedResponseTest(request["expectedResponse"]))

        if('dataTypeCheck' in request.keys()):
            teststring += str(addDataTypeTest(request["dataTypeCheck"], fieldPrefix))


        return teststring

def createPreRequestString(request,prerequeststring ):
          
          prerequeststring += endpointComparePreRequisite(request)
          return prerequeststring

def populateCollection(test_filename):
#Reading the input JSON file
    test_filename = os.path.split(test_filename)
    test_file_path = os.path.join(test_filename[0], 'jsons', test_filename[-1])
    with open(test_file_path) as requests:
        requests = json.load(requests)
    
    jsonRequest = []

# Looping through all the requests in the input file and adding all of the relevant data to the list of requests. 
    
    for i in requests:
        prerequeststring = ''
        #Adding Base Tests and Variables
        teststring = ' var response = pm.response.json(); \n var request = JSON.parse(request.data); \n pm.test("Status code is 200", function () {pm.response.to.have.status(200);}); \n \n pm.test("Response time is less than 10s", function () {pm.expect(pm.response.responseTime).to.be.below(10000);}); \n \n '


        i["requestBody"] = json.dumps(i["requestBody"])
        requestUrl = i["requestUrl"]
        if('compareUrl' in i.keys()):
          compareUrl = i["compareUrl"]
          prerequeststring += createPreRequestString(compareUrl, prerequeststring)
        teststring = createTestString(i, teststring, "response.out_dev_all.")
        

            # Creating the Individual Requests
        pm_url_raw = ""
        pm_url_protocol = ""
        pm_url_host = []
        pm_url_path = []

        url_parts = re.search(r'^([^:]+)://([^/]+)/?(.*)$', requestUrl)
        pm_url_raw = url_parts[0]
        pm_url_protocol = url_parts[1]
        pm_url_host = url_parts[2].split('.')
        pm_url_path = url_parts[3].split('/')

        jsonRequest.append({"name":i["testName"],"event":[{"listen":"prerequest","script":{"exec":[prerequeststring],"type":"text/javascript"}},{"listen":"test","script":{"exec":[ teststring ],"type":"text/javascript"}}],"request":{"method":"POST","header":[{"key": "X-RE-Test-Name", "value" : i["testName"] + " " + str(datetime.now())}],"body":{"mode":"raw","raw":i["requestBody"],"options":{"raw":{"language":"json"}}},"url":{"raw":pm_url_raw,"protocol":pm_url_protocol,"host":pm_url_host,"path":pm_url_path}},"response":[]})
        
    return jsonRequest


if __name__ == "__main__":

  # Create the parser
  my_parser = argparse.ArgumentParser(description='Run JSON API Testfile')

# Add the arguments
#Argument to provide path to where Json Test file is
  my_parser.add_argument('-p', '--path')
#Argument to determine whether to write results to newman file or not (provide either 'json' or 'csv' as argument)
  my_parser.add_argument('-f', '--file')
#Argument to decide to actually run the collection via NewMan
  my_parser.add_argument("-e", '--execute')

  
# Execute the parse_args() method
  args = my_parser.parse_args()
  executeImmediately = args.execute
  userchoice = args.path
  if(userchoice == None):
    userchoice = input("please Specify the path to the Json Test File")

 


  userchoice = os.path.normpath(userchoice)
  if ".xlsx"  in userchoice:
    read_excel(userchoice)
    print("It should print here")
    
    userchoice = userchoice.replace(".xlsx", ".json")
    print(userchoice + "(Chekc here")
  basedata =  populateCollection(userchoice)
  
  newmanPath = os.path.normpath(userchoice.replace(".json", "_collection.json"))
#  if(executeImmediately != "false"):
#    os.system("newman run " + newmanPath)
   
    

  if(args.file != None):
    workingdir = os.path.normpath("../results")
    os.chdir(workingdir)
    newmanPath = os.path.normpath("../collectiongenerator/json_data.json ")
    if(args.file != "text"):
#      os.system("newman run " + newmanPath +" -r" + args.file)
        pass
    else:
      newmanProcess = subprocess.run("newman run " + newmanPath, shell=True, capture_output=True)
      resultFile = open('Results_'+datetime.now().strftime("%H:%M:%S - %b %d %Y").replace(' ','').replace('-','_').replace(':',';')+'.txt', "w", encoding="utf-8" )
      print("stdout = " + newmanProcess.stdout.decode("utf-8"), file = resultFile)
      resultFile.close()
    #If you want to log to CSV