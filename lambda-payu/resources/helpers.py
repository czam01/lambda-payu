"""Helper functions for the lambda payu"""
import re
# import pycountry
import hashlib
import time
import datetime

regex_card_type = [
    {"regex": "^4[0-9]{12}(?:[0-9]{3})?$", "card_name": "VISA"},
    {"regex": "^3(?:0[0-5]|[68][0-9])[0-9]{11}$", "card_name": "DINERS"},
    {"regex": "^3[47][0-9]{13}$", "card_name": "AMEX"},
    {
        "regex": "^65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(?:12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})$",
        "card_name": "DISCOVER"},
    {"regex": "^5[1-5][0-9]{14}$", "card_name": "MASTERCARD"},
    {"regex": "^(603493)(?:[0-9]{10})$", "card_name": "CENCOSUD"},
    {"regex": "^(590712)(?:[0-9]{10})$", "card_name": "CODENSA"},
]


def find_card_type(card_number):
    """
    Credit and Debit cards (Authorization and capture) Available franchises: Credit( Visa, Mastercard,
     Amex, Diners and Codensa) and Debit( Visa Debit ).
     """
    for i in regex_card_type:
        if re.match(i["regex"], card_number):
            return i["card_name"]
    return "GET_PAYMENT_METHOD"


def get_country_code(country):
    if len(country) > 2:
        # country = "Colombia"
        # country_code = pycountry.countries.get(name=country.title())
        return "CO"  # country_code.alpha_2
    else:
        return "CO"


def create_signature(api_key, merchant_id, reference_code, tx_value, currency):
    # Para API: transaction.order.signature
    # "ApiKey~merchantId~referenceCode~tx_value~currency"
    to_encrypt_array = [api_key, merchant_id, reference_code, tx_value, currency]
    print(to_encrypt_array)
    string_to_encrypt = '~'.join(to_encrypt_array)
    encrypted_message = hashlib.md5(str.encode(string_to_encrypt))
    return encrypted_message.hexdigest()


def set_credit_card_validation_digits(value):
    if find_card_type(value) == "AMEX":
        return "0000"
    else:
        return "000"


def create_reference_code(cc_number):
    ts = str(round(time.time() * 1000))
    reference_code = "-".join([cc_number, ts])
    print(reference_code)
    return reference_code


def get_current_date(ts_milliseconds):
    return datetime.datetime.fromtimestamp(ts_milliseconds / 1000.0)


def get_current_date_error():
    ts = int(round(time.time() * 1000))
    return datetime.datetime.fromtimestamp(ts / 1000.0)


def get_date_format_request(phone_date):
    phone_date_format = phone_date[:4] + "/" + phone_date[4:] \
        if len(phone_date[4:]) == 2 \
        else phone_date[:4] + "/" + "0" + phone_date[4:]
    return phone_date_format
