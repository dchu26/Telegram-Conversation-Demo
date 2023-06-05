# Telegram-Archive
 
 Instructions on how to use:
 
 Obtain an api id and api hash from Telethon
 
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

