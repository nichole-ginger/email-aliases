from __future__ import print_function
import os.path
import csv
import itertools
import re

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from vars import customer_id, domain_alias, parent_domain_name

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.domain']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token-domains.json'):
        creds = Credentials.from_authorized_user_file('token-domains.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token-domains.json', 'w') as token:
            token.write(creds.to_json())

    google = build('admin', 'directory_v1', credentials=creds)

    body = {
        "kind": "admin#directory#domainAlias",
        "domainAliasName": domain_alias,
        "parentDomainName": parent_domain_name
    }

    # List all domains FIRST before modifying
    # results = google.domains().list(customer=f'{customer_id}').execute()

    # Insert Domain Alias
    results = google.domainAliases().insert(customer=f'{customer_id}', body=body).execute()
    print(results)


if __name__ == '__main__':
    main()