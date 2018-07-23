import os
import json
import requests
import boto3
from base64 import b64decode

# field to search
# https://www.zoho.com/crm/help/api/v2/#ra-search-records
"""
Only one of the above four parameters would work at one point of time.
Furthermore, if two parameters are given simultaneously, preference will be given in the order criteria,
email, phone and word, and only one of them would work.
"""

ZOHO_CRM_URL = os.environ['ZOHO_CRM_URL']
ZOHO_AUTHORIZATION = (
boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['ZOHO_AUTHORIZATION']))['Plaintext']).decode("utf-8")


def zoho_user_parser(user_json):
    user_json = json.loads(user_json)
    user_json = user_json["data"][0]
    user_details = {
        "CC_client": user_json["Home_Phone"],
        "Transaction_Value": user_json["Other_Phone"],
        "Transaction_Currency": user_json["Fax"],
        "Email": user_json["Email"],
        "Mailing_Zip": user_json["Mailing_Zip"],
        "Mailing_State": user_json["Mailing_State"],
        "Mailing_Street": user_json["Mailing_Street"],
        "First_Name": user_json["First_Name"],
        "Asst_Phone": user_json["Asst_Phone"],
        "Full_Name": user_json["Full_Name"],
        "Department": user_json["Department"],
        "Description": user_json["Description"],
        "Phone": user_json["Phone"],
        "Mailing_Country": user_json["Mailing_Country"],
        "Date_of_Birth": user_json["Date_of_Birth"],
        "Mailing_City": user_json["Mailing_City"],
        "Other_Street": user_json["Other_Street"],
        "Mobile": user_json["Mobile"],
        "Home_Phone": user_json["Home_Phone"],
        "Last_Name": user_json["Last_Name"],
        "status": True
    }
    return user_details


def zoho_handle_user(request_json):
    if request_json.status_code == 200:
        return zoho_user_parser(request_json.text)
    else:
        request_details = dict()
        request_details["message"] = "User not found on the CRM" if request_json.status_code == 204 else "Unknown Error"
        request_details["status"] = False
        return request_details


def zoho_get_user_details(cc_number):
    querystring = {"word": cc_number}
    headers = {
        'Authorization': ZOHO_AUTHORIZATION,
    }
    response = requests.request("GET", ZOHO_CRM_URL, headers=headers, params=querystring)
    return zoho_handle_user(response)
