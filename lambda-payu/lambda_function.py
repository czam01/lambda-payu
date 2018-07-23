import json
import boto3
from base64 import b64decode, b64encode
from resources import zoho_crm as zhcrm
from resources import payu_request_object
from resources import dynamo_reporter
from resources import helpers


def handle_response_payu(payu_response, connect_details, user_data_crm):
    response_pay = json.loads(payu_response)
    if response_pay.get('transactionResponse'):
        if response_pay.get('transactionResponse', {}).get('responseCode') == "APPROVED":
            dynamo_reporter.payment_approved_report(response_pay, connect_details, user_data_crm)
            return_json={"status": "success"}
            print ("Approved response")
            print (return_json)
            return return_json
    dynamo_reporter.payment_error_report(response_pay, connect_details, user_data_crm)
    # response_pay["transactionResponse"]["responseMessage"]
    return_json={"status": "failure"}
    print ("Rejected response")
    print (return_json)
    return return_json
        

def main_function(connect_details):
    user_data_crm = zhcrm.zoho_get_user_details(connect_details["cc_numero"])
    if user_data_crm["status"]:
        print(user_data_crm)
        payu_response = payu_request_object.payu_main_request(connect_details, user_data_crm)
        return handle_response_payu(payu_response, connect_details, user_data_crm)

    else:
        # used on the case if theres no data on zoho crm
        print("User Not found on zoho crm end  please ask to start again")
        return_json={"status": "failure"}
        print ("Rejected response")
        print (return_json)
        return return_json


def lambda_handler(event, context):
    """ lambda good practices, avoid code on the handler"""
    print("+++++++++++++base event++++++++++++++++++++++++")
    print(event)
    print("++++++++++++++++++++++++++++++++++++++++++++++")
    event_parameters = event['Details']['Parameters']
    event_contact_data = event['Details']['ContactData']['Attributes']
    #"4097440000000004"  #
    tc_card =(boto3.client('kms').decrypt(CiphertextBlob=b64decode(event_parameters['tc_numero']))['Plaintext']).decode("utf-8")
    user_details = {"cc_numero": event_contact_data['cc_numero'], "tc_numero": tc_card,
                    "tc_number_payments": event_contact_data['tc_cuotas'],
                    "tc_fecha": helpers.get_date_format_request(event_contact_data['tc_fecha'])}
    user_details["tc_reference_code"] = helpers.create_reference_code(user_details["cc_numero"])
    return main_function(user_details)
