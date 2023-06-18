import os
import re
import json
import csv
import ast
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict
from telethon import events
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from google.cloud import secretmanager

# Scope for the Google service account
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# ADD BELOW HERE #


##################

# Credentials from Google cloud account
credentials = ServiceAccountCredentials.from_json_keyfile_dict(client_json, scope)
gclient = gspread.authorize(credentials)

# Credentials for user
api_id = anon_json["API_ID"]
api_hash = anon_json["API_HASH"]

# Initiates the client, which is basically the account associated with the id and hash
# 'anon' can be changed, this is just the name of the .session file
client = TelegramClient('anon', api_id, api_hash)

# Names of the people whom you've had a conversation with
dialog_names = []

# Database for our entries (key = Telegram user id, value = all other attributes)
database = defaultdict(dict)

# Name of the Google Sheet
sheet_name = 'CSV-to-Google-Sheet'

# Listener for new messages
@client.on(events.NewMessage())
async def handler(event):
    print(type(database[5748872509]['email']))
    # Twitter name holder
    t = []
    # Email holder
    e = []
    # LinkedIn link holder
    l = []
    # Person who messaged
    messenger = event.message.peer_id.user_id
    # Full info of messenger
    fullInfo = await client(GetFullUserRequest(messenger))
    # Parsing for relevant info
    twitter_finder(event.message.message, t)
    email_finder(event.message.message, e)
    linkedin_finder(event.message.message, l)

    # Situation where we need to make a new entry in our database (new user messages us)
    if messenger not in database:
        database[messenger]["first_name"] = fullInfo.users[0].first_name
        database[messenger]["last_name"] = fullInfo.users[0].last_name
        database[messenger]["username"] = fullInfo.users[0].username
        database[messenger]["phone"] = fullInfo.users[0].phone
        database[messenger]["twitter"] = t
        database[messenger]["email"] = e
        database[messenger]["linkedin"] = l

    # Entry is already in our database
    else:
        database[messenger]["twitter"].extend(t)
        database[messenger]["email"].extend(e)
        database[messenger]["linkedin"].extend(l)

    # Updates the csv file again
    await dic_to_csv()

    # Updates the Google sheet
    await csv_to_google()


############################################################################


# Function that gets information from Google Sheet and populates our database
async def google_to_dict():
    # Opening the spreadsheet on the first sheet
    spreadsheet = gclient.open(sheet_name).sheet1
    # Getting data from spreadsheet
    data = spreadsheet.get_all_records()
    
    # Getting data for each row
    for record in data:
        # Get the first key-value pair
        first_key = next(iter(record))
        # Getting the key-value records and storing as a dict, excluding the first key-value pair
        record_without_first = {key: value for key, value in record.items() if key != first_key}
        # Initializing database using User ID as the key, and record_without_first as the value
        database[record[first_key]] = record_without_first
    
    # Converting the string representation of the lists into lists when applicable
    # ast.literal_eval() is quite strict on conversion so we have to check if it is valid to convert before we actually do it
    for key in database:
        if is_valid_list_string(database[key]['linkedin']):
            database[key]['linkedin'] = ast.literal_eval(database[key]['linkedin'])
        if is_valid_list_string(database[key]['email']):
            database[key]['email'] = ast.literal_eval(database[key]['email'])
        if is_valid_list_string(database[key]['twitter']):
            database[key]['twitter'] = ast.literal_eval(database[key]['twitter'])


# Function for moving data from dictionary to CSV file
async def dic_to_csv():
    # Write dictionary into csv file
    
    # Initializing each column name
    csv_columns = ['User ID', 'first_name', 'last_name',
                   'username', 'phone', 'linkedin', 'email', 'twitter']
    
    # Try to open the csv file and write to it
    try:
        with open("database.csv", "w") as csvfile:
            # Writing the data to the csv file with these parameters
            writer = csv.DictWriter(
                csvfile, fieldnames=csv_columns, lineterminator='\n')
            # Creating the header in the CSV file
            writer.writeheader()
            # Writing everything else
            for key, val in database.items():
                # Creating key-value with the User ID key
                row = {'User ID': key}
                row.update(val)
                writer.writerow(row)
    # Any possible error that occurs with opening the csv file
    except IOError:
        print("I/O error")


# Basic function to write csv data to the Google sheet
async def csv_to_google():
    # Opens the spreadsheet
    spreadsheet = gclient.open(sheet_name)

    # Reading and writing to the Google Sheet
    with open('database.csv', 'r') as file_obj:
        content = file_obj.read()
        gclient.import_csv(spreadsheet.id, data=content)


# Helper function for checking if a string representation of a list can be converted into a list
def is_valid_list_string(string_representation):
    # Situation where it is possible to do so
    try:
        ast.literal_eval(string_representation)
        return True
    # Situation where the input is invalid for ast.literal_eval()
    except (SyntaxError, ValueError):
        print(string_representation)
        return False

# Function for adding names to dialog_names
async def name_finder():
    async for dialog in client.iter_dialogs():
        # print(dialog.name, 'has ID', dialog.id)
        dialog_names.append(dialog.name)


# Function for adding emails parsed from a string to emails
def email_finder(text, emails):
    # Regex expression to match for emails
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    emails.extend(match)


# Function for adding twitter username parsed from a string to twitter_names
def twitter_finder(str, twitter_name):
    # Regex expression to match for twitter usernames
    same = re.findall(r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))(@[A-Za-z0-9-_]+)', str)
    twitter_name.extend(same)


# Function for adding linkedin links parsed from a string to linkedin_links
def linkedin_finder(s, linkedin_links):
    # Regex expression for only linkedin links
    regex = r'(https?:\/\/[\w]+\.?linkedin\.com\/in\/[A-z0-9_-]+\/?)'
    urls = re.findall(regex, s)
    linkedin_links.extend(urls)


# Main function
async def main():

    # Pulling data from Google Sheets and populating our database (dict)
    await google_to_dict()
    # Moving our data from the dict into the CSV
    await dic_to_csv()


# Runs until main is complete for now, then runs begins event handling
with client:
    client.loop.run_until_complete(main())
    client.start()
    client.run_until_disconnected()