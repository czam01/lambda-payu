import os
from boto3 import resource
from resources import helpers

dynamodb_resource = resource('dynamodb')

PAYMENT_ERROR_TRANSACTIONS = os.environ['payUErrorTable']
PAYMENT_HISTORY = os.environ['payUPaymentsHistory']


def add_item(table_name, col_dict):
    """
    Add one item (row) to table. col_dict is a dictionary {col_name: value}.
    """
    table = dynamodb_resource.Table(table_name)
    response = table.put_item(Item=col_dict)

    return response


def payment_approved_report(response, connect_details, user_data_crm):
    user_object = dict()
    user_object["reference_code"] = connect_details["tc_reference_code"]
    user_object["cc_numero"] = user_data_crm["CC_client"]
    user_object["user_name"] = user_data_crm["Full_Name"]
    user_object["transaction_value"] = user_data_crm["Transaction_Value"]
    user_object["payu_orderId"] = response["transactionResponse"]["orderId"]
    user_object["payu_transaction_id"] = response["transactionResponse"]["transactionId"]
    user_object["payu_operation_date"] = str(helpers.get_current_date(response["transactionResponse"]["operationDate"]))
    
    add_item(PAYMENT_HISTORY, user_object)


def payment_error_report(response, connect_details, user_data_crm):
    response_transaction = response["transactionResponse"]
    if response_transaction:
        user_object = dict()
        user_object["reference_code"] = connect_details["tc_reference_code"]
        user_object["cc_numero"] = user_data_crm["CC_client"]
        user_object["user_name"] = user_data_crm["Full_Name"]
        user_object["payu_orderId"] = response["transactionResponse"]["orderId"]
        user_object["payu_transaction_id"] = response["transactionResponse"]["transactionId"]
        user_object["response_code"] = response["transactionResponse"]["responseCode"]
        user_object["response_message"] = response["transactionResponse"]["responseMessage"]
        user_object["payu_operation_date"] = str(helpers.get_current_date_error())
        add_item(PAYMENT_ERROR_TRANSACTIONS, user_object)
    else:
        user_object = dict()
        user_object["reference_code"] = connect_details["tc_reference_code"]
        user_object["cc_numero"] = user_data_crm["CC_client"]
        user_object["user_name"] = user_data_crm["Full_Name"]
        user_object["response_code"] = response["code"]
        user_object["response_message"] = response["error"]
        user_object["payu_operation_date"] = str(helpers.get_current_date_error())
        add_item(PAYMENT_ERROR_TRANSACTIONS, user_object)
        
