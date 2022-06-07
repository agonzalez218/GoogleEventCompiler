import datetime
import os.path
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import timedelta, date

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


def displayList(calendarsString, my_list):
    stringEvents = ""
    stringDates = ""
    newWindow = Toplevel(root)
    newWindow.title("Results")
    newWindow.geometry("500x300")
    varDates = StringVar()
    varEvents = StringVar()
    varCalendars = StringVar(value=calendarsString)
    labelCalendars = Label(newWindow, textvariable=varCalendars, relief=RAISED)
    labelDate = Label(newWindow, textvariable=varDates, relief=RAISED)
    labelEvent = Label(newWindow, textvariable=varEvents, relief=RAISED)
    for index, value in enumerate(my_list):
        if index % 2 == 0:
            stringDates += (my_list[index]) + "\n"
            stringEvents += (my_list[index + 1]) + "\n"
    varEvents.set(stringEvents)
    varDates.set(stringDates)
    labelCalendars.grid(column=0, columnspan=2, row=0)
    labelDate.grid(column=0, row=1)
    labelEvent.grid(column=1, row=1)


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
                if varType == "numEvents":
                    events_result = service.events().list(calendarId=calendar, timeMin=now,
                                                          maxResults=int(numEvents.get().replace(" ", "")), singleEvents=True,
                                                          orderBy='startTime').execute()
                elif varType == "numDays":
                    # 2022-06-06T16:15:00-05:00
                    events_result = service.events().list(calendarId=calendar, timeMin=now,
                                                          timeMax=str(date.today()+datetime.timedelta(days=int(numDays.get())))+"T00:00:00-05:00", singleEvents=True,
                                                          orderBy='startTime').execute()
                elif varType == "endDate":
                    # 2022-06-06T16:15:00-05:00
                    events_result = service.events().list(calendarId=calendar, timeMin=now,
                                                          timeMax=endDate.get()+"T00:00:00-05:00", singleEvents=True,
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
        displayList(string, eventList)

    except HttpError as error:
        print('An error occurred: %s' % error)


def startProcess():
    if selected.get() == " ":
        tkinter.messagebox.showerror(title="Event Search Error", message="No search type selected")
    elif selected.get() == "endDate" and endDate.get() == "":
        tkinter.messagebox.showerror(title="Event Search Error", message="No input provided for type selected")
    elif selected.get() == "numDays" and numDays.get() == "":
        tkinter.messagebox.showerror(title="Event Search Error", message="No input provided for type selected")
    elif selected.get() == "numEvents" and numEvents.get() == "":
        tkinter.messagebox.showerror(title="Event Search Error", message="No input provided for type selected")
    else:
        creds = accessAPI()
        accessEvents(creds, selected.get())


root = Tk(className=" Event and Reminder App")
root.geometry("450x150")
frm = ttk.Frame(root, padding=10)
frm.grid()
selected = tkinter.StringVar(value=" ")
endDate = tkinter.StringVar(value="")
numDays = tkinter.StringVar(value="")
numEvents = tkinter.StringVar(value="")

tkinter.Radiobutton(frm, text='Search for events until End Date (yyyy-mm-dd)', value='endDate', variable=selected).grid(column=0,
                                                                                                               row=0)
tkinter.Radiobutton(frm, text='Search for number of upcoming events', value='numEvents', variable=selected).grid(column=0,
                                                                                                          row=1)
tkinter.Radiobutton(frm, text='Search for events in number of upcoming days', value='numDays', variable=selected).grid(column=0,
                                                                                                          row=2)
ttk.Entry(frm, textvariable=endDate).grid(column=1, row=0)
ttk.Entry(frm, textvariable=numEvents).grid(column=1, row=1)
ttk.Entry(frm, textvariable=numDays).grid(column=1, row=2)
ttk.Button(frm, text="Search", command=lambda: startProcess()).grid(column=0, row=3)
ttk.Button(frm, text="Exit", command=lambda: root.destroy()).grid(column=1, row=3)
root.mainloop()
