import os.path
import pickle

from colr import color as co
from colr import hex2rgb
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """
    retrieve colorIDs from Google Calendar API and display them.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gcalendar', 'v3', credentials=creds)
    colors = service.colors().get().execute()

    # Print available calendarListEntry colors.
    for id, color in colors['gcalendar'].items():
        # print('colorId: %s' % id)
        # print('Background: %s' % color['background'])
        # print('Foreground: %s' % color['foreground'])
        # use colr library to print coloured text in terminal
        print(co('###colorId: {}###'.format(id), fore=hex2rgb(color['foreground']), back=hex2rgb(color['background'])))

    # Print available event colors.
    # for id, color in colors['event'].items():
    #     print(co(id, fore=hex2rgb(color['foreground']), back=hex2rgb(color['background'])))

    # print('colorId: %s' % id)
    #     print('Background: %s' % color['background'])
    #     print('Foreground: %s' % color['foreground'])


if __name__ == '__main__':
    main()
