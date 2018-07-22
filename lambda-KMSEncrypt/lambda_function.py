import boto3
import json
import os
import base64
from base64 import b64decode, b64encode
kms_client = boto3.client('kms')

KMSKEY = kms_client.decrypt(CiphertextBlob=b64decode(os.environ['KMSKEY']))['Plaintext']
KMSKEY = KMSKEY.decode('utf-8')

def lambda_handler(event, context):
    tc_number = event['Details']['Parameters']['tc_numero']
    tc_number = b = tc_number.encode('utf-8')
    encrypted = kms_client.encrypt(KeyId=KMSKEY,Plaintext= tc_number )
    binary_encrypted = encrypted[u'CiphertextBlob']
    encrypted_card = base64.b64encode(binary_encrypted)
    return {'tc_numero':encrypted_card.decode("utf-8")}
