# Telegram-Archive
 
 Instructions on how to use:
 
## Signing In

Before working with Telegram’s API, you need to get your own API ID and hash:

1. Login to your Telegram account with the phone number of the developer account to use.
2. Click under API Development tools.
3. A *Create new application* window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (*App title* and *Short name*) can currently be changed later.
4. Click on *Create application* at the end. Remember that your **API hash is secret** and Telegram won’t let you revoke it. Don’t post it anywhere!
 
 Create a file called ".env" and add the id and hash in like so:
 
 API_ID = replace with id
 
 API_HASH = 'replace with hash'
 
 
pip3 install telethon

pip3 install python-dotenv

## Telethon Installation

Telethon is a Python library, which means you need to download and install Python from https://www.python.org/downloads/ if you haven’t already. Once you have Python installed, upgrade pip and run:

```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade telethon
```

…to install or upgrade the library to the latest version.

### Installing Development Versions

If you want the *latest* unreleased changes, you can run the following command instead:

```
python3 -m pip install --upgrade https://github.com/LonamiWebs/Telethon/archive/v1.zip

```

### Verification

To verify that the library is installed correctly, run the following command:

```
python3 -c "import telethon; print(telethon.__version__)"
```

The version number of the library should show in the output.

### Optional Dependencies 

If [cryptg](https://github.com/cher-nov/cryptg) is installed, **the library will work a lot faster**, since encryption and decryption will be made in C instead of Python. If your code deals with a lot of updates or you are downloading/uploading a lot of files, you will notice a considerable speed-up (from a hundred kilobytes per second to several megabytes per second, if your connection allows it). If it’s not installed, [pyaes](https://github.com/ricmoo/pyaes) will be used (which is pure Python, so it’s much slower).

If [pillow](https://python-pillow.org/) is installed, large images will be automatically resized when sending photos to prevent Telegram from failing with “invalid image”. Official clients also do this.

If [aiohttp](https://docs.aiohttp.org/en/stable/) is installed, the library will be able to download [WebDocument](https://tl.telethon.dev/constructors/web_document.html) media files (otherwise you will get an error).

If [hachoir](https://hachoir.readthedocs.io/en/latest/) is installed, it will be used to extract metadata from files when sending documents. Telegram uses this information to show the song’s performer, artist, title, duration, and for videos too (including size). Otherwise, they will default to empty values, and you can set the attributes manually.

## CSV to Google Sheet

We are going to use [gspread](https://gspread.readthedocs.io/en/latest/), which is a Python API for Google Sheets.

For interacting with Google Sheet API first thing we have to do is create a project in [Google Developers Console](https://medium.com/craftsmenltd/from-csv-to-google-sheet-using-python-ef097cb014f9#:~:text=For%20interacting%20with%20Google%20Sheet%20API%20first%20thing%20we%20have%20to%20do%20is%20create%20a%20project%20in%20Google%20Developers%20Console%20and%20enable%20some%20APIs.%20To%20do%20that%20just%20follow%20the%20steps%20below.) and enable some APIs. To do that just follow the steps below.

1. Click [here](https://console.developers.google.com/cloud-resource-manager) to create a project.
2. Give the project a name.
3. Go to project dashboard and click on + **ENABLE APIS AND SERVICES**.
4. Search for **Google Drive API** and click on it.
5. Enable Google Drive API.
6. Click on **Create Credentials**.
7. Select the parameters and click on **What credentials do I need?**.
- **Which API are you using?** Google Drive API
* **What data will you be accessing?** Application Data
+ **Are you planning to use this API with Compute Engine, Kubernetes Engine, App Engine, or Cloud Functions?** No, I'm not using them
9. Enter a Service Account Name and select Role as *Editor*
10. Return to the *Credentials* tab in the project dashboard
11. Press the pencil nect to the service account name
12. Above *Service account details*, locate and click on **KEYS**
13. Press ADD KEY, *Create new key*, make sure *Key type* is JSON and press *Create*.

A JSON file will be downloaded. We will need this JSON file in our script. So rename that file as *client_secret.json*. The content of the JSON file is as following:

```
{
  "type": "service_account",
  "project_id": "focus-zxzxzx-******",
  "private_key_id": "****************************************",
  "private_key": "-----BEGIN PRIVATE KEY-----\n***private_key***\n-----END PRIVATE KEY-----\n",
  "client_email": "google-sheet-demo@focus-zxzxzx-******.iam.gserviceaccount.com",
  "client_id": "************************",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheet-demo%40focus-zxzxzx-******.iam.gserviceaccount.com"
}
```

Go to your Google Drive and create an Google Sheet and name it **CSV-to-Google-Sheet**. Copy *client_email* value from the JSON file you have downloaded above and share that Google Sheet to this *client_email* with edit permission.

Open up the terminal and run the following commands.

```
pip3 install gspread
pip3 install oauth2client
```

Now create a Python file and name it upload.py. Copy and paste the following code in it.

```
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('CSV-to-Google-Sheet')

with open('database.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
```

Run the Python script with this command 
```
python3 upload.py 
```
Next, open **CSV-to-Google-Sheet** Google Sheet in your browser. 

The complete code to help can be found in [this repository](https://github.com/nahidsaikat/CSV-to-Google-Sheet).
