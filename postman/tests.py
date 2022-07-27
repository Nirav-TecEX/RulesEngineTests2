import json
import re
import jsbeautifier

def jsEscapeValue(val):
    if val is None:
        return "null"
    elif isinstance(val, bool):
        if(val == True):
          return "true"
        else:
          return "false"
    
    elif isinstance(val, str):
        esc_val = re.sub(r'([\\\'\"])', r'\\\1', val)
        # Converts this <a href="/a4J1v000000I2E7EAK" target="_blank">R-0719</a>
        # to this: <a href=\"/a4J1v000000I2E7EAK\" target=\"_blank\">R-0719</a>
        #
        # Also this: "How are you \ ok fine" 'or not'
        # To this: \"How are you \\ ok fine \" \'or not\'
        esc_val = esc_val.replace("\n", "\\n").replace("\t","\\t").replace("\r","\\r").replace("\f","\\f")
        return "'" + esc_val + "'"
    else:
        return val

def prepareObjectToString(val):
    val = str(val)
    val = re.sub("(\"')|('\")", "'", val)
    val = re.sub("'true'", 'true', val)
    val = re.sub("'false'", 'false', val)
    val = re.sub("'null'", 'null', val)
    # val = re.sub("\[", "[\n", val)
    # val = re.sub("},", "},\n", val)
    # val = re.sub("{", "{\n", val)
    return val

def addValueTest(testValues, fieldPrefix=""):
 
  valueTestJs = ''
  taskTests = []
  costingTests = []
  rateTests = []
  for z in testValues:
    
    excelTaskPos = re.search(".?Task\[(.*)]", z["fieldName"]) 
    excelCostingPost = re.search(".?CPA_Costing__c\[(.*)]", z["fieldName"])
    excelRatePos = re.search(".?r__Courier_Rate__c\[(.*)]", z["fieldName"])
    
    if z["fieldValue"] is not None and isinstance(z["fieldValue"],(str)) and  z["fieldValue"].startswith('*'):
      valueTestJs +=  'pm.test("Checking if ' +str(z["fieldName"]) + ' equals ' + str(jsEscapeValue(z["fieldValue"])) +' (After Making it a list)", function () {var requestString = ' + jsEscapeValue(z["fieldValue"]) +';var responselist = ' + fieldPrefix+ str(z["fieldName"]) + '.sort(); requestString = requestString.substring(1);let inputArray = requestString.split(",");inputArray = inputArray.sort();let boolPass = true;for(let i = 0; i < inputArray.length; i++){if(inputArray[i] != responselist[i] ){boolPass = false;}}if(inputArray.length != responselist.length){boolPass = false;}pm.expect(boolPass).to.equal(true); });'
    elif excelTaskPos is None and excelCostingPost is None and excelRatePos is None:
      if(z["fieldValue"] != "undefined" and z["fieldValue"] != "!null"):
        valueTestJs += 'pm.test("Checking if ' +str(z["fieldName"]) + ' equals ' + str(jsEscapeValue(z["fieldValue"])) +'" , function () { if(typeof ' + fieldPrefix+ str(z["fieldName"]) + ' == "number"){pm.expect(Math.round(10e2 * ' + fieldPrefix+ str(z["fieldName"]) + ') / 10e2).to.eql(Math.round(10e2 *  ' + str(jsEscapeValue(z["fieldValue"])) +') / 10e2);}else{pm.expect(' + fieldPrefix+ str(z["fieldName"]) + ').to.eql(' + str(jsEscapeValue(z["fieldValue"])) +');}});'
      elif(z["fieldValue"] == "!null"):
        valueTestJs += 'pm.test("Checking if C' +str(z["fieldName"]) + '  equals !null", function() {pm.expect(' + fieldPrefix+ str(z["fieldName"]) + ').to.not.eql(null);});' 
      else:
        valueTestJs += 'pm.test("Checking if ' +str(z["fieldName"]) + ' equals undefined", function() { try {pm.expect(pm.expect(' + fieldPrefix+ str(z["fieldName"]) + ').to.eql(undefined));    } catch {if ("' + fieldPrefix+ str(z["fieldName"]) + '".slice(-1) == "]") { pm.expect('+ fieldPrefix+ str(z["fieldName"])[0:str(z["fieldName"]).rfind("[")]  + ').to.eql(undefined);} else {pm.expect(' + fieldPrefix+ str(z["fieldName"]) + ').to.be.empty;}}});'
        #valueTestJs += 'pm.test("Checking if ' +str(z["fieldName"]) + ' equals undefined" , function () { try { pm.expect(' + fieldPrefix+ str(z["fieldName"]) + ').to.eql(undefined); }catch{pm.expect(' + fieldPrefix+ str(z["fieldName"])[0:str(z["fieldName"]).rfind("[")]  + ').to.eql(undefined); }});'
    elif excelTaskPos is not None :
      responseHierarchy = re.search(".*(?=\[)", z["fieldName"]).group(0)
      excelTaskPos = re.search(".?Task\[(.*)]", z["fieldName"]).group(1)
      taskTests.append({})
      taskTests[int(excelTaskPos)][re.search("\]\.(.*)",z["fieldName"]).group(1)] = jsEscapeValue(z["fieldValue"])
    elif excelCostingPost is not None :
      responseHierarchy = re.search(".*(?=\[)", z["fieldName"]).group(0)
      excelCostingPost = re.search(".?CPA_Costing__c\[(.*)]", z["fieldName"]).group(1)
      costingTests.append({})
      costingTests[int(excelCostingPost)][re.search("\]\.(.*)",z["fieldName"]).group(1)] = jsEscapeValue(z["fieldValue"])
    elif excelRatePos is not None:
      responseHierarchy = re.search(".*(?=\[)", z["fieldName"]).group(0)
      excelRatePos = re.search(".?r__Courier_Rate__c\[(.*)]", z["fieldName"]).group(1)
    
      rateTests.append({})
      rateTests[int(excelRatePos)][re.search("\]\.(.*)", re.search("\]\.(.*)",z["fieldName"]).group(1)).group(1)] = jsEscapeValue(z["fieldValue"])

  
  taskTests = [object for object in taskTests if object != {}]
  costingTests = [object for object in costingTests if object != {}]
  rateTests = [object for object in rateTests if object != {}]
  
  if(len(costingTests) != 0):
    costingTests = prepareObjectToString(costingTests)
    valueTestJs += ' var response = pm.response.json(); var jsonData = pm.response.json();let excelTestCostingList = '+costingTests+';let responseCostingList = jsonData.out_dev_all.'+ responseHierarchy +';let excelTestCostingResultList = Array(excelTestCostingList.length).fill(false);let excelTestMapping = Array(excelTestCostingList.length);let responseCostingUsedList = Array(responseCostingList.length).fill(false);let excelTestCostingIndex = 0;excelTestCostingList.forEach(eachExcelCosting => {    let responseCostingIndex = 0;  responseCostingList.forEach(eachResponseCosting => { if (!responseCostingUsedList[responseCostingIndex]) { if (eachExcelCosting.Costing_Name__c == eachResponseCosting.Costing_Name__c) {          excelTestMapping[excelTestCostingList.indexOf(eachExcelCosting)] = responseCostingList.indexOf(eachResponseCosting);               excelTestCostingResultList[excelTestCostingIndex] = true;responseCostingUsedList[responseCostingIndex] = true;}} responseCostingIndex++;});  excelTestCostingIndex++;});/*Testing Begins Here*/for (let i = 0; i < excelTestMapping.length; i++) {if (excelTestMapping[i] != null) {    for (let key in excelTestCostingList[i]) {            pm.test("Excel Test Costing[" + i + "].  " + key + " equals Response Costing[" + excelTestMapping[i] + "]." + key + " (Name: " + excelTestCostingList[i]["Costing_Name__c"] + ")", function() {                pm.expect(excelTestCostingList[i][key]).to.equal(responseCostingList[excelTestMapping[i]][key])});} }}for (let i = 0; i < responseCostingUsedList.length; i++) { if (responseCostingUsedList[i] == false) {        pm.test("No Tests for Response Costing[" + i + "]" + " (Name: " + responseCostingList[i]["Costing_Name__c"] + ")", function() {            pm.expect(responseCostingUsedList[i]).to.equal(true); });    }}for (let i = 0; i < excelTestCostingResultList.length; i++) { if (excelTestCostingResultList[i] == false) { pm.test("Excel Costing[" + i + "] included in Response" + " (Name: " + excelTestCostingList[i]["Costing_Name__c"] + ")", function() { pm.expect(excelTestCostingResultList[i]).to.equal(true);}); }}pm.test("Amount of Costings in Excel == Amount of Costings in Response", function() {    pm.expect(excelTestCostingList.length).to.equal(responseCostingList.length);});'
  if(len(taskTests) != 0):
    taskTests = prepareObjectToString(taskTests)
    valueTestJs += 'var jsonData = pm.response.json(); \n let excelTestTaskList = '+ taskTests+'; \n \nlet responseTaskList = jsonData.out_dev_all.'+responseHierarchy+'; \n let excelTestTaskResultList = Array(excelTestTaskList.length).fill(false); \n let excelTestMapping = Array(excelTestTaskList.length); \n let responseTaskUsedList = Array(responseTaskList.length).fill(false); \n let excelTestTaskIndex = 0; \n \n excelTestTaskList.forEach(eachExcelTask => { \n \nlet responseTaskIndex = 0; \n responseTaskList.forEach(eachResponseTask => { \n \n if(!responseTaskUsedList[responseTaskIndex]){ \n if(eachExcelTask.Master_Task__c == eachResponseTask.Master_Task__c && eachExcelTask.Description == eachResponseTask.Description && eachExcelTask.Part__c == eachResponseTask.Part__c && eachExcelTask.Package__c == eachResponseTask.Package__c && eachExcelTask.Final_Delivery__c == eachResponseTask.Final_Delivery__c  ){ \n excelTestMapping[excelTestTaskList.indexOf(eachExcelTask)] = responseTaskList.indexOf(eachResponseTask); \n excelTestTaskResultList[excelTestTaskIndex] = true; \n responseTaskUsedList[responseTaskIndex] = true; \n } \n } \n responseTaskIndex++; \n }); \n excelTestTaskIndex++; \n}); \n \n /*Testing Begins Here*/ \n for (let i = 0; i < excelTestMapping.length; i++) { \n if (excelTestMapping[i] != null) { \n for (let key in excelTestTaskList[i]) { \n pm.test("Excel Test Task[" + i + "].  " + key + " equals Response Task[" + excelTestMapping[i] + "]." + key + " (Master Task: " + excelTestTaskList[i]["Master_Task__c"] + ")", function() { \n pm.expect(excelTestTaskList[i][key]).to.equal(responseTaskList[excelTestMapping[i]][key]) \n });} \n } \n } \n for (let i = 0; i < responseTaskUsedList.length; i++) { \n if (responseTaskUsedList[i] == false) { \n pm.test("No Tests for Response Task[" + i + "]" + " (Master Task: " + responseTaskList[i]["Master_Task__c"] + ")", function() { \n pm.expect(responseTaskUsedList[i]).to.equal(true); \n }); \n } \n } \nfor (let i = 0; i < excelTestTaskResultList.length; i++) { \n if (excelTestTaskResultList[i] == false) { \n pm.test("Excel Task[" + i + "] included in Response" + " (Master Task: " + excelTestTaskList[i]["Master_Task__c"] + ")", function() { \n pm.expect(excelTestTaskResultList[i]).to.equal(true); \n }); \n } \n } \n pm.test("Amount of Tasks in Excel == Amount of Tasks in Response", function() { \n pm.expect(excelTestTaskList.length).to.equal(responseTaskList.length); \n });'
  if(len(rateTests) != 0):
    rateTests = prepareObjectToString(rateTests)
    
    valueTestJs += 'var response = pm.response.json(); var jsonData = pm.response.json(); let excelRateList = ' + rateTests + ' ; let responseRateList = jsonData.out_dev_all.Shipment_Order__c.r__Freight__c[0].r__Courier_Rate__c; let excelTestRateResultList = Array(excelRateList.length).fill(false); let excelTestMapping = Array(excelRateList.length); let responseRateUsedList = Array(responseRateList.length).fill(false); let excelTestRateIndex = 0; excelRateList.forEach(eachExcelRate => { let responseRateIndex = 0; responseRateList.forEach(eachResponseRate => { if (!responseRateUsedList[responseRateIndex]) { if (eachExcelRate.service_type__c == eachResponseRate.service_type__c && eachExcelRate.Origin__c == eachResponseRate.Origin__c ) { excelTestMapping[excelRateList.indexOf(eachExcelRate)] = responseRateList.indexOf(eachResponseRate); excelTestRateResultList[excelTestRateIndex] = true; responseRateUsedList[responseRateIndex] = true; } } responseRateIndex++; }); excelTestRateIndex++; }); /*Testing Begins Here*/ for (let i = 0; i < excelTestMapping.length; i++) { if (excelTestMapping[i] != null) { for (let key in excelRateList[i]) { if(key != "Rate__c" && key != "Final_Rate__c" && key != "Stream_Rate__c"){ pm.test("Excel Test Rate[" + i + "]. " + key + " equals Response Rate[" + excelTestMapping[i] + "]." + key + " (Name: " + excelRateList[i]["Costing_Name__c"] + ")", function() { pm.expect(excelRateList[i][key]).to.equal(responseRateList[excelTestMapping[i]][key]) }); }else{  pm.test("Excel Test Rate[" + i + "]. " + key + " equals Response Rate[" + excelTestMapping[i] + "]." + key + " (Name: " + excelRateList[i]["Costing_Name__c"] + ")", function() { pm.expect(responseRateList[excelTestMapping[i]][key]).to.be.below(excelRateList[i][key] * 1.05); pm.expect(responseRateList[excelTestMapping[i]][key]).to.be.above( excelRateList[i][key]* 0.95) }); } } } } for (let i = 0; i < responseRateUsedList.length; i++) { if (responseRateUsedList[i] == false) { pm.test("No Tests for Response Costing[" + i + "]" + " (Name: " + responseRateList[i]["Costing_Name__c"] + ")", function() { pm.expect(responseRateUsedList[i]).to.equal(true); }); } } for (let i = 0; i < excelTestRateResultList.length; i++) { if (excelTestRateResultList[i] == false) { pm.test("Excel Costing[" + i + "] included in Response" + " (Name: " + excelRateList[i]["Costing_Name__c"] + ")", function() { pm.expect(excelTestRateResultList[i]).to.equal(true); }); } } pm.test("Amount of Costings in Excel == Amount of Costings in Response", function() { pm.expect(excelRateList.length).to.equal(responseRateList.length); });'
  valueTestJs = jsbeautifier.beautify(valueTestJs)
  return valueTestJs


def addFieldCheckTest(testFields, fieldPrefix=""):
  valueTestJs = ''
  for z in testFields:
    valueTestJs += 'pm.test(\"Check if ' +str(z["fieldName"]) + '  is in Response\", function () {pm.expect(' +fieldPrefix+str(z["fieldName"]) + ').to.not.be.empty;});'
    #response[0].soId
  return valueTestJs


def addContainTest(testFields, fieldPrefix=""):
  valueTestJs = ''
  for z in testFields:
    valueTestJs += 'pm.test(\"Check if ' +str(z["fieldName"]) + ' contains ' + jsEscapeValue(z["fieldValue"]) +'\", function () {pm.expect((' +fieldPrefix+str(z["fieldName"]) + ')).to.include(' + jsEscapeValue(z["fieldValue"]) +');});'
    #response[0].soId
  return valueTestJs


def addNumCompareTest(testFields, fieldPrefix=""):
    valueTestJs = ''
    for z in testFields:
        valueTestJs += 'pm.test(\"Checking if ' + z["fieldName"] + ' ' + z["operator"] + ' ' +  z["value"] + '\", function () { var testPass = false;if(' + fieldPrefix+z["fieldName"] + z["operator"] + str(z["value"]) + '){testPass = true;}pm.expect(testPass).to.eql(true);});'
    #response[0].soId
    return valueTestJs


def addDataTypeTest(testFields, fieldPrefix=""):
    valueTestJs = ''
    for z in testFields:
      valueTestJs += 'pm.test(\"Checking Datatype of ' + z["fieldName"] + ' is ' + z["dataType"] + '\", function () {pm.expect(typeof(' + fieldPrefix+z["fieldName"] + ')).to.eql(' + z["dataType"] + ');});'                                     
    return valueTestJs;


def addExpectedResponseTest(ExpectedResult):
    ExpectedResultStr = json.dumps(ExpectedResult)
    valueTestJs = '' 
    valueTestJs +=  "var expectedResponse = " + ExpectedResultStr+ ";function diff(obj1, obj2) {const result = {};    if (Object.is(obj1, obj2)) {return undefined;}if (!obj2 || typeof obj2 !== 'object') {return obj2;}Object.keys(obj1).concat(Object.keys(obj2)).forEach(key => {if (obj2[key] !== obj1[key] && !Object.is(obj1[key], obj2[key])) {result[key] = obj2[key];}if (typeof obj2[key] === 'object' && typeof obj1[key] === 'object') {const value = diff(obj1[key], obj2[key]);if (value !== undefined) {result[key] = value;}}});return result;}if (!Object.is(response,expectedResponse )) {const result = diff(expectedResponse, response);const expectedResult = diff(response, expectedResponse);pm.test(\"Check Expected Response\", function() {pm.expect(JSON.stringify(result)).to.equal(JSON.stringify(expectedResult));});}"
							
    return valueTestJs


def endpointCompareTestString():
    valueTestJs = '' 
    valueTestJs +=  "const stagingReponse = pm.collectionVariables.get('stagingResponse');const prodResponse = pm.response.json();var emptyString = '{\"0\":{\"parts\":{\"0\":{}}}}';function diff(obj1, obj2) {const result = {};    if (Object.is(obj1, obj2)) {return undefined;}if (!obj2 || typeof obj2 !== 'object') {return obj2;}Object.keys(obj1).concat(Object.keys(obj2)).forEach(key => {if (obj2[key] !== obj1[key] && !Object.is(obj1[key], obj2[key])) { result[key] = obj2[key];}if (typeof obj2[key] === 'object' && typeof obj1[key] === 'object') {const value = diff(obj1[key], obj2[key]);if (value !== undefined) {result[key] = value;}}});return result;} if (!Object.is(prodResponse, JSON.parse(pm.collectionVariables.get('stagingResponse')))) {const result = diff(JSON.parse(pm.collectionVariables.get('stagingResponse')), prodResponse); const expectedResult = diff(JSON.parse(pm.collectionVariables.get('stagingResponse')), JSON.parse(pm.collectionVariables.get('stagingResponse')));pm.test(\"Check Difference\", function() {pm.expect(JSON.stringify(expectedResult)).to.equal(JSON.stringify(result));});}"
							
    return valueTestJs


def endpointComparePreRequisite(TestValues):
    valueTestJS = ''
    valueTestJS += 'const interval = setTimeout(() => {}, 100);let promiseNumber = 0;const postRequest = {url: '+TestValues+', method: "POST", async: false, header: {"Content-Type": "application/json","X-Foo": "bar"},body: pm.request.body};function resolvedPromise() {return new Promise((resolve, reject) => {pm.sendRequest(postRequest, (err, res) => {if (err) {console.log(err);  reject();} else {console.log(`Resolved promise ${++promiseNumber}`);pm.collectionVariables.set(\"stagingResponse\",JSON.stringify(JSON.parse(new Buffer.from(res.stream).toString())));resolve();}});});}resolvedPromise().then(resolvedPromise).then(resolvedPromise).then(() => clearTimeout(interval)).catch(err => console.log(err));clearTimeout(interval);'
    return valueTestJS

#Timeout Originially set to Number.MAX_SAFE_INTEGER but this had issues as it was larger than 32 bit signed int can handle

    						
    




