import datetime
import os.path
import tkinter
from tkinter import *
from tkinter import ttk

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def sortFunc(my_list):
    new_list = []
    index = 0
    while my_list:
        minVal = my_list[0]
        name = my_list[1]
        for index, value in enumerate(my_list):
            if index % 2 == 0:
                if my_list[index] < minVal:
                    minVal = my_list[index]
                    name = my_list[index + 1]
        new_list.append(minVal)
        new_list.append(name)
        my_list.remove(minVal)
        my_list.remove(name)

    my_list = new_list
    return my_list


def printList(my_list):
    for index, value in enumerate(my_list):
        if index % 2 == 0:
            print(my_list[index], my_list[index + 1])


def accessAPI():
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
    return creds


def accessEvents(creds, varType):
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        page_token = None
        events = []
        calendars = []
        eventList = []
        counter = 0
        string = "The following Calendars were used: "
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            # Iterate through User's subscribed calendar list
            for calendar_list_entry in calendar_list['items']:
                calendar = calendar_list_entry['id']
                calendars.append(calendar_list_entry['summary'])
                counter += 1
                # Get all events from calendar until a specified timeMax date
                if varType == "num":
                    events_result = service.events().list(calendarId=calendar, timeMin=now,
                                                          maxResults=int(num.get().replace(" ", "")), singleEvents=True,
                                                          orderBy='startTime').execute()
                elif varType == "endDate":
                    # 2022-06-06T16:15:00-05:00
                    events_result = service.events().list(calendarId=calendar, timeMin=now,
                                                          timeMax=endDate.get()+"T16:15:00-05:00", singleEvents=True,
                                                          orderBy='startTime').execute()
                events += events_result.get('items', [])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        if not events:
            print('No upcoming events found.')
            return

        # Adds start and name of events to list, sorts by time, then prints list
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            eventList += (start, event['summary'])
        eventList = sortFunc(eventList)
        for i in range(counter):
            string += calendars[i]
            if i != counter - 1:
                string += ", "
        print(string)
        printList(eventList)

    except HttpError as error:
        print('An error occurred: %s' % error)


def startProcess():
    creds = accessAPI()
    accessEvents(creds, selected.get())


root = Tk(className=" Event and Reminder App")
root.geometry("400x150")
frm = ttk.Frame(root, padding=10)
frm.grid()
selected = tkinter.StringVar(value=' ')
endDate = tkinter.StringVar()
num = tkinter.StringVar()

tkinter.Radiobutton(frm, text='Search for events until End Date', value='endDate', variable=selected).grid(column=0,
                                                                                                               row=0)
tkinter.Radiobutton(frm, text='Search for # of upcoming events', value='num', variable=selected).grid(column=0,
                                                                                                          row=1)
ttk.Entry(frm, textvariable=endDate).grid(column=1, row=0)
ttk.Entry(frm, textvariable=num).grid(column=1, row=1)
ttk.Button(frm, text="Start Process", command=lambda: startProcess()).grid(column=0, row=2)
ttk.Button(frm, text="Exit", command=lambda: root.quit).grid(column=1, row=2)
root.mainloop()
