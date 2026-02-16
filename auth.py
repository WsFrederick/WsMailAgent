# auth.py
from O365 import Account
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
SECRET_VALUE = os.getenv("SECRET_VALUE")
TENANT_ID = os.getenv("TENANT_ID")

SCOPES = [
    'https://graph.microsoft.com/Mail.Read',
    'https://graph.microsoft.com/Mail.ReadWrite',
    'offline_access'
]

def get_account():
    credentials = (CLIENT_ID, SECRET_VALUE)
    account = Account(credentials, tenant_id=TENANT_ID)

    if not account.is_authenticated:
        account.authenticate(scopes=SCOPES)

    return account