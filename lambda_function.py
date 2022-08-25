from time import sleep
import requests
from requests.auth import HTTPBasicAuth
import random
import json
import jsonpickle


#
# Variables
#

# General
headers = {"Content-Type": "application/json", "accept": "application/json"}

# WHS
whsApi = "https://xxxx/"    # FGT API
whsUser = "WHS000002"       # DID
whsPassword = "password"
whsBasicAuth = HTTPBasicAuth(whsUser, whsPassword)

# PHA
phaApi = "https://xxxx/"    # FGT API
phaUser = "PHA000002"       # DID
phaPassword = "password"
phaBasicAuth = HTTPBasicAuth(phaUser, phaPassword)

shipments = []
newShipments = []
sales = []

successRequests = 0
errorRequests = 0


#
# Functions
#

def evaluateResponse(response):
    if response.status_code == 200:
        global successRequests
        successRequests += 1
    else:
        global errorRequests
        errorRequests += 1
        print(response.text)


#
# Execution
#

def lambda_handler(event, context):

    # GET all MAH -> WHS shipments

    response = requests.get(whsApi + "traceability/shipment/getAll?itemPerPage=1000&sort=dsc&requesterId=" + whsUser, auth=whsBasicAuth, headers=headers)
    evaluateResponse(response)

    responstJSON = jsonpickle.decode(json.dumps(response.json()))
    shipmentList = responstJSON.get("results")


    # PUT updates on all WHS shipments to "received" and "confirmed"

    for shipment in shipmentList:
        status = shipment.get("status").get("status")
        shipmentId = shipment.get("shipmentId")
        shipmentIdOnly = shipment.get("shipmentId").rsplit('-', 1)[1]  # currently not used

        if status == "delivered":
            payload = {'status':'received', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(whsApi + "traceability/shipment/update/" + shipmentId, auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)

        if status == "delivered" or status == "received":
            payload = {'status':'confirmed', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(whsApi + "traceability/shipment/update/" + shipmentId, auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)

            newShipments.append(shipment)


    # POST shipments WHS -> PHA

    for shipment in newShipments:
        shipmentId = random.randint(10000000,99999999)
        shipmentLines = []
        for line in shipment.get("shipmentLines"):
            shipmentLines.append({'gtin':str(line.get("gtin")), 'batch': str(line.get("batch")),  'quantity':line.get("quantity")})

        payload = {'shipmentId':str(shipmentId), 'requesterId': str(phaUser), 'shipmentLines':shipmentLines}
        response = requests.post(whsApi + "traceability/shipment/create", auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
        evaluateResponse(response)


    # GET all WHS -> PHA shipments

    response = requests.get(whsApi + "traceability/shipment/getAll?itemPerPage=1000&sort=dsc&senderId=" + whsUser, auth=whsBasicAuth, headers=headers)
    evaluateResponse(response)

    responstJSON = jsonpickle.decode(json.dumps(response.json()))
    shipmentList = responstJSON.get("results")

    # PUT updates on all WHS -> PHA shipments (pickup, transit, delivered)

    for shipment in shipmentList:
        status = shipment.get("status").get("status")
        shipmentId = shipment.get("shipmentId")

        if status == "created":
            payload = {'status':'pickup', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(whsApi + "traceability/shipment/update/" + shipmentId, auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)

        if status == "created" or status == "pickup":
            payload = {'status':'transit', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(whsApi + "traceability/shipment/update/" + shipmentId, auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)
        
        if status == "created" or status == "pickup" or status == "transit":
            payload = {'status':'delivered', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(whsApi + "traceability/shipment/update/" + shipmentId, auth=whsBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)


    # Sleep to allow PHA to receive shipment information
    if len(newShipments) > 0:
        sleep(15)

    # GET all PHA shipments

    response = requests.get(phaApi + "traceability/shipment/getAll?itemPerPage=1000&sort=dsc&requesterId=" + phaUser, auth=phaBasicAuth, headers=headers)

    responstJSON = jsonpickle.decode(json.dumps(response.json()))
    shipmentList = responstJSON.get("results")
    evaluateResponse(response)


    # PUT updates on all PHA shipments (received, confirmed)

    for shipment in shipmentList:
        status = shipment.get("status").get("status")
        shipmentId = shipment.get("shipmentId")

        if status == "delivered":
            payload = {'status':'received', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(phaApi + "traceability/shipment/update/" + shipmentId, auth=phaBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)

        if status == "delivered" or status == "received":
            payload = {'status':'confirmed', 'extraInfo':'Automated update by AWS Lambda'}
            response = requests.put(phaApi + "traceability/shipment/update/" + shipmentId, auth=phaBasicAuth, headers=headers , data = json.dumps(payload))
            evaluateResponse(response)


    # GET all PHA stocks

    response = requests.get(phaApi + "traceability/stock/getAll?itemPerPage=1000&sort=dsc&requesterId=" + phaUser, auth=phaBasicAuth, headers=headers)

    responstJSON = jsonpickle.decode(json.dumps(response.json()))
    stockList = responstJSON.get("results")
    evaluateResponse(response)

    # POST sales to all available PHA stocks
    ## Currently still in development - not functioning yet

    for stock in stockList:
        gtinNumber = stock.get("gtin")

        for batch in stock.get("batches"):
            saleId = random.randint(10000000,99999999)
            payload = {'id':str(saleId), 'productList':[{'gtin':str(gtinNumber), 'batchNumber':str(batch.get("batchNumber")), 'serialNumber':'XXXX'}]}
            # response = requests.post(phaApi + "traceability/sale/create", auth=phaBasicAuth, headers=headers , data = json.dumps(payload))
            # evaluateResponse(response)


    result = "Script completed - Total Requests: " + str(successRequests + errorRequests) + " Successes: " + str(successRequests) + " Errors: " + str(errorRequests)
    print(result)

    return result

# Remove comment to run locally
# lambda_handler("","")