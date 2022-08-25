# PharmaLedger FGT Shipment Robot
This repository provides an AWS lambda function to automate shipment processes and product dispense.

### What the shipment robot does

- **Wholesaler (WHS)**
  - "Receive" & "Confirm" any shipments that are on the status "delivered"
  - Create new shipments to the specified Pharmacy (PHA)
  - Update the the shipment status to "pickup", "transit" and "delivered"
- **Pharmacy (PHA)**
  - "Receive" & "Confirm" any shipments that are on the status "delivered"
  - (in development) Sell any available products on stock



### How to use it - locally or in AWS

1. Clone the repository
2. Add the correct URL, DID/Username and password to the configuration for the WHS and PHA of your choice to `lambda_function.py`
3. Run the `lambda_function.py` locally to test if it is working (--> temporarily remove comment from the last line at the bottom)
4. Login to the AWS CLI
5. Adjust the function name and region with your preferences in the `deploy_lambda.sh`
5. Deploy the lambda function via the `deploy_lambda.sh` script
6. Create a rule on AWS EventBridge to regularly run the lambda function