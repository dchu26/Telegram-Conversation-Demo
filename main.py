import os
import re
from collections import defaultdict
from telethon import events
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from dotenv import load_dotenv, find_dotenv

# Loads the .env file
load_dotenv(find_dotenv())

# Retrieves the API_ID and API_HASH from the .env file
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")

# Initiates the client, which is basically the account associated with the id and hash
# 'anon' can be changed, this is just the name of the .session file
client = TelegramClient('anon', api_id, api_hash)

# Names of the people whom you've had a conversation with
database = defaultdict(dict)
dialog_names = []

# Listener for new messages
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    t = []
    e = []
    l = []
    twitter_finder(event.message.message, t)
    email_finder(event.message.message, e)
    linkedin_finder(event.message.message, l)
    database[event.message.peer_id.user_id]["twitter"].extend(t)
    database[event.message.peer_id.user_id]["email"].extend(e)
    database[event.message.peer_id.user_id]["linkedin"].extend(l)
    print(database)

# Function for adding names to dialog_names
async def name_finder():
    async for dialog in client.iter_dialogs():
        #print(dialog.name, 'has ID', dialog.id)
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
    url = re.findall(regex, s)
    linkedin_links.extend(url)

# Main function
async def main():

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
            print("Group Chat called {}".format(name))

    # Where the population of the database into a different file should be
    print(database)

# Runs until main is complete for now, then runs begins event handling
with client:
    client.loop.run_until_complete(main())
    client.start()
    client.run_until_disconnected()