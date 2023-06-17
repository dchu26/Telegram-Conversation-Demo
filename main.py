import os
import ast
import re
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict
from telethon import events
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from dotenv import load_dotenv, find_dotenv

# Scope for the Google service account
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Credentials from Google cloud account
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
gclient = gspread.authorize(credentials)

# Loads the .env file
load_dotenv(find_dotenv())

# Retrieves the API_ID and API_HASH from the .env file
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")

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
    dic_to_csv()

    # Updates the Google sheet
    csv_to_google()


############################################################################


# Function that gets information from Google Sheet and populates our database
def google_to_dict():
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
    for key in database:
        if is_valid_list_string(database[key]['linkedin']):
            database[key]['linkedin'] = ast.literal_eval(database[key]['linkedin'])
        if is_valid_list_string(database[key]['email']):
            database[key]['email'] = ast.literal_eval(database[key]['email'])
        if is_valid_list_string(database[key]['twitter']):
            database[key]['twitter'] = ast.literal_eval(database[key]['twitter'])


# Function for moving data from dictionary to CSV file
def dic_to_csv():
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
def csv_to_google():
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

    # Commented out due to redundancy
    '''
    workingLinks = []

    # Validate linkedin links
    for url in urls:
        validation = validators.url(url)
        if validation:
            workingLinks.append(url)

    linkedin_links.extend(workingLinks)
    '''


# Main function
async def main():

    google_to_dict()
    dic_to_csv()
    
    '''
    # Previous main function, gathers information from history of 1 on 1 chats
    
    # Populates dialog_names
    await name_finder()

    # Gets the full profile information for the first user in each conversation
    for name in dialog_names:
        try:
            userInfo = await client(GetFullUserRequest(name))
            user = userInfo.users[0]
            database[user.id]["first_name"] = user.first_name
            database[user.id]["last_name"] = user.last_name
            database[user.id]["username"] = user.username
            database[user.id]["phone"] = user.phone

            emails = []
            twitter_name = []
            linkedin_links = []

            async for message in client.iter_messages(name):
                email_finder(message.text, emails)
                twitter_finder(message.text, twitter_name)
                linkedin_finder(message.text, linkedin_links)

            database[user.id]["linkedin"] = linkedin_links
            database[user.id]["email"] = emails
            database[user.id]["twitter"] = twitter_name

        # Exception when the group chat is named
        except Exception as e:
            print()
            #print("Group Chat called {}".format(name))

    # Where the population of the database into a csv file happens
    # print(database)
    dic_to_csv()
    
    csv_to_google()
    '''

# Runs until main is complete for now, then runs begins event handling
with client:
    client.loop.run_until_complete(main())
    client.start()
    client.run_until_disconnected()
