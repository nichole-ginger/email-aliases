from __future__ import print_function
import os.path
import csv
import itertools

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from vars import domain, organization

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('admin', 'directory_v1', credentials=creds)

    # Call the Admin SDK Directory API
    results = service.users().list(domain, maxResults=500,
                                orderBy='email').execute()
    users = results.get('users', [])
    usersList = []
    nextPageToken = None
    emailsDict = {}
    csvCount = 0
    header = []
    rowCount = 0

    if not users:
        print('No users in the domain.')
    else:
        for user in users:
            usersList.append(user['primaryEmail'])
        # If more than 500 users are returned do this:  
        if 'nextPageToken' in results:
            nextPageToken = results['nextPageToken']
            nextCall = service.users().list(domain, maxResults=500,
                                orderBy='email', pageToken=nextPageToken).execute()
            users2 = nextCall.get('users', [])
            if users2:
                for user in users2:
                    usersList.append(user['primaryEmail'])
            allUsers = users + users2

            # Uncomment this print and then redirect STDOUT to json file for all user info
            # print(allUsers)

            count = 0
            for user in allUsers:
                emailsDict[count] = {}
                badAliases = []
                goodAliases = []
                if not (("DEPARTED" in user['name']['fullName']) or ("Departed" in user['name']['fullName']) or ("Terminated" in user['name']['fullName']) or ("departed" in user['primaryEmail']) or ( user['suspended'] == True) or (user['archived'] == True)):
                    emailsDict[count]['Name'] = user['name']['fullName']
                    emailsDict[count]['Primary Email'] = user['primaryEmail']
                    emailsDict[count]['Aliases'] = user['emails']
                    if "care.ginger.io" in user['primaryEmail']:
                        for email in user['emails']:
                            alias = dict(itertools.islice(email.items(), 1))
                            for k, v in alias.items():
                                if ("fin.ginger.com" in v) or ("fin.ginger.io" in v) or ("ext.ginger.com" in v) or ("ext.ginger.io" in v):
                                    badAliases.append(v)
                                else:
                                    goodAliases.append(v)
                            emailsDict[count]['Bad Aliases'] = badAliases
                            emailsDict[count]['Good Aliases'] = goodAliases
                            emailsDict[count]['Missing Alias'] = [user['primaryEmail'][:-2] + "com"]
                        count += 1
                    else:
                        for email in user['emails']:
                            alias = dict(itertools.islice(email.items(), 1))
                            for k, v in alias.items():
                                if ("fin.ginger.com" in v) or ("fin.ginger.io" in v) or ("ext.ginger.com" in v) or ("ext.ginger.io" in v) or ("care.ginger.io" in v) or ("care.ginger.com" in v):
                                    badAliases.append(v)
                                else:
                                    goodAliases.append(v)
                            emailsDict[count]['Bad Aliases'] = badAliases
                            emailsDict[count]['Good Aliases'] = goodAliases
                            emailsDict[count]['Missing Alias'] = []
                        count += 1

        else:
            count = 0
            for user in users:
                emailsDict[count] = {}
                badAliases = []
                goodAliases = []
                if not (("DEPARTED" in user['name']['fullName']) or ("Departed" in user['name']['fullName']) or ("Terminated" in user['name']['fullName']) or ("departed" in user['primaryEmail']) or (user['suspended'] == True) or (user['archived'] == True)):
                    emailsDict[count]['Name'] = user['name']['fullName']
                    emailsDict[count]['Primary Email'] = user['primaryEmail']
                    emailsDict[count]['Aliases'] = user['emails']
                    if "care.ginger.io" in user['primaryEmail']:
                        for email in user['emails']:
                            alias = dict(itertools.islice(email.items(), 1))
                            for k, v in alias.items():
                                if ("fin.ginger.com" in v) or ("fin.ginger.io" in v) or ("ext.ginger.com" in v) or ("ext.ginger.io" in v):
                                    badAliases.append(v)
                                else:
                                    goodAliases.append(v)
                        emailsDict[count]['Bad Aliases'] = badAliases
                        emailsDict[count]['Good Aliases'] = goodAliases
                        emailsDict[count]['Missing Alias'] = [user['primaryEmail'][:-2] + "com"]
                        count += 1
                    else:
                        for email in user['emails']:
                            alias = dict(itertools.islice(email.items(), 1))
                            for k, v in alias.items():
                                if ("fin.ginger.com" in v) or ("fin.ginger.io" in v) or ("ext.ginger.com" in v) or ("ext.ginger.io" in v) or ("care.ginger.io" in v) or ("care.ginger.com" in v):
                                    badAliases.append(v)
                                else:
                                    goodAliases.append(v)
                            emailsDict[count]['Bad Aliases'] = badAliases
                            emailsDict[count]['Good Aliases'] = goodAliases
                            emailsDict[count]['Missing Alias'] = []
                        count += 1

        with open("all-emails-final.csv", "w") as file:
            w = csv.writer( file )
            for employeeInt, value in emailsDict.items():
                for i in value:
                    if csvCount <= 5:
                        header.append(i)
                        csvCount += 1
                    if csvCount == 6:
                        w.writerow(header)
                        csvCount += 1
                row = []
                for key, item in value.items():
                    if rowCount <= 1:
                        row.append(item)
                    addressList = []
                    if rowCount == 2:
                        for k in item:
                            if type(k) == 'dict':
                                addressList.append(k['address'])
                            else:
                                addressList.append(k)

                        row.append(addressList)
                    if rowCount == 3:
                        row.append(item)
                    if rowCount == 4:
                        row.append(item)
                    if rowCount == 5:
                        row.append(item)
                        w.writerow(row)
                    rowCount += 1
                    if rowCount == 6:
                        rowCount = 0
        file.close()


if __name__ == '__main__':
    main()