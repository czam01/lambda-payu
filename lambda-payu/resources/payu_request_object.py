import json
import requests
import boto3
import os
from base64 import b64decode
from resources import helpers

PAYU_MERCHANT_API_KEY = (
boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['PAYU_MERCHANT_API_KEY']))['Plaintext']).decode("utf-8")
PAYU_MERCHAN_API_LOGIN = (
boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['PAYU_MERCHAN_API_LOGIN']))['Plaintext']).decode(
    "utf-8")
PAYU_MERCHANT_ID = (
boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['PAYU_MERCHANT_ID']))['Plaintext']).decode("utf-8")
PAYU_ACCOUNT_ID = (
boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['PAYU_ACCOUNT_ID']))['Plaintext']).decode("utf-8")
PAYU_COUNTRY_CODE = os.environ['PAYU_COUNTRY_CODE']
PAYU_URL = os.environ['PAYU_URL']
TEST_MODE = os.environ['TEST_MODE']

headers = {
    'Content-Type': "application/json",
    "Accept": "application/json"
}


class PayUObjectRequest:
    def __init__(self, language, command, test):
        self.language = language
        self.command = command
        self.test = test

    def set_transaction(self, transaction):
        self.transaction = transaction

    def set_merchant(self, merchant_details):
        self.merchant = merchant_details


class Merchant:
    def __init__(self, merchant_api_key, merchant_api_login):
        self.apiKey = merchant_api_key
        self.apiLogin = merchant_api_login


class Buyer:
    def __init__(self, full_name, email_address, contact_phone, dni_number):
        self.fullName = full_name
        self.emailAddress = email_address
        self.contactPhone = contact_phone
        self.dniNumber = dni_number

    def add_shipping_address(self, shipping_address_details):
        self.shippingAddress = shipping_address_details


class ShippingAddress:
    def __init__(self, street1, city, state, country, postal_code):
        self.street1 = street1
        self.city = city
        self.state = state
        self.country = country
        self.postalCode = postal_code


class Order:
    def __init__(self, account_id, reference_code, description, signature):
        self.accountId = account_id
        self.referenceCode = reference_code
        self.description = description
        self.language = "es"
        self.signature = signature

    def add_shipping_address(self, shipping_address_details):
        self.shippingAddress = shipping_address_details

    def add_buyer(self, buyer_details):
        self.buyer = buyer_details

    def add_additional_values(self, additional_values_details):
        self.additionalValues = additional_values_details


class TransactionAdditionalValue:
    def __init__(self, transaction_value, transaction_currency, value=0, currency_ret="COP"):
        self.TX_VALUE = {
            "value": transaction_value,
            "currency": transaction_currency
        }

        # if no defined default values
        self.TX_TAX_RETURN_BASE = {
            "value": value,
            "currency": currency_ret
        }
        
        self.TX_TAX = {
            "value": value,
            "currency": currency_ret
        }

class Payer:
    def __init__(self, full_name, email_address, contact_phone, dni_number):
        self.fullName = full_name
        self.emailAddress = email_address
        self.contactPhone = contact_phone
        self.dniNumber = dni_number

    def add_billing_address(self, billing_address_details):
        self.billingAddress = billing_address_details


class BillingAddress:
    def __init__(self, street1, city, state, country, postal_code):
        self.street1 = street1
        self.city = city
        self.state = state
        self.country = country
        self.postalCode = postal_code


class CreditCard:
    def __init__(self, number, expiration_date, name):
        self.number = number
        self.securityCode = helpers.set_credit_card_validation_digits(self.number)
        self.expirationDate = expiration_date
        self.name = name
        self.processWithoutCvv2 = True

    def get_credit_card_type(self):
        return helpers.find_card_type(self.number)


class Transaction:
    def __init__(self, type_transaction, payment_method, payment_country):
        self.type = type_transaction
        self.paymentMethod = payment_method
        self.paymentCountry = payment_country
        self.deviceSessionId = ""
        self.ipAddress = "127.0.0.1"
        self.cookie = ""
        self.userAgent = ""

    def add_order(self, order_details):
        self.order = order_details

    def add_payer(self, payer_details):
        self.payer = payer_details

    def add_credit_card(self, credit_card_details):
        self.creditCard = credit_card_details

    def add_extra_parameters(self, extra_parameters):
        self.extraParameters = extra_parameters


class ExtraParameters:
    def __init__(self, number_payments):
        self.INSTALLMENTS_NUMBER = number_payments


def payu_main_request(connect_details, user_data_crm):
    base_object = PayUObjectRequest("es", "SUBMIT_TRANSACTION", helpers.get_bool_from_env(TEST_MODE))  # Test Mode
    merchant = Merchant(PAYU_MERCHANT_API_KEY, PAYU_MERCHAN_API_LOGIN)
    credit_card = CreditCard(connect_details["tc_numero"],
                             connect_details["tc_fecha"],user_data_crm["Full_Name"])  # "REJECTED")  # "APPROVED")#

    transaction = Transaction("AUTHORIZATION_AND_CAPTURE", credit_card.get_credit_card_type(), PAYU_COUNTRY_CODE)

    payer = Payer(user_data_crm["Full_Name"], user_data_crm["Email"], user_data_crm["Mobile"],
                  user_data_crm["CC_client"])

    billing_address = BillingAddress(user_data_crm["Mailing_Street"], user_data_crm["Mailing_City"],
                                     user_data_crm["Mailing_State"],
                                     helpers.get_country_code(user_data_crm["Mailing_Country"]),
                                     user_data_crm["Mailing_Zip"])

    signature = helpers.create_signature(PAYU_MERCHANT_API_KEY, PAYU_MERCHANT_ID,
                                         connect_details["tc_reference_code"]
                                         , user_data_crm["Transaction_Value"],
                                         user_data_crm["Transaction_Currency"])

    order = Order(PAYU_ACCOUNT_ID, connect_details["tc_reference_code"], user_data_crm["Description"], signature)

    buyer = Buyer(user_data_crm["Full_Name"], user_data_crm["Email"], user_data_crm["Mobile"],
                  user_data_crm["CC_client"])

    shipping_address = ShippingAddress(user_data_crm["Mailing_Street"], user_data_crm["Mailing_City"],
                                       user_data_crm["Mailing_State"],
                                       helpers.get_country_code(user_data_crm["Mailing_Country"]),
                                       user_data_crm["Mailing_Zip"])
    tx_additional_values = TransactionAdditionalValue(user_data_crm["Transaction_Value"],
                                                      user_data_crm["Transaction_Currency"])
    extra_parameters = ExtraParameters(connect_details["tc_number_payments"])

    buyer.add_shipping_address(vars(shipping_address))
    order.add_shipping_address(vars(shipping_address))
    order.add_buyer(vars(buyer))
    order.add_additional_values(vars(tx_additional_values))
    payer.add_billing_address(vars(billing_address))

    transaction.add_payer(vars(payer))
    transaction.add_credit_card(vars(credit_card))
    transaction.add_order(vars(order))
    transaction.add_extra_parameters(vars(extra_parameters))

    base_object.set_merchant(vars(merchant))
    base_object.set_transaction(vars(transaction))

    print(json.dumps(vars(base_object)))

    request_json = json.dumps(vars(base_object))
    response = requests.request("POST", PAYU_URL, data=request_json, headers=headers)
    print(response.text)
    return response.text
