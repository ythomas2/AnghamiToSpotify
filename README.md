# Anghami to Spotify Playlist Migration
This Python script allows you to migrate playlists from Anghami to Spotify. 

It utilizes the Spotify API, along with the BeautifulSoup and Spotipy libraries, to fetch the playlist information and copy it to your Spotify account.

## Prerequisites
Before running this script, ensure that you have the following installed on your machine:

1. Python 3.x
2. pip (Python package installer)

Additionally, make sure to install the required dependencies by running the following commands in your command prompt:

`
python3 -m venv ./venv
`

`
pip install -r requirements.txt
`

## Getting Started
Follow the steps listed below to begin the playlist migration:
### Extraction
#### Method 1
1. Navigate to the playlist (or downloads and likes) you want to duplicate on Anghami's web player. Make sure that all the songs are loaded and viewable in the queue. This can be done by clicking on the first song, pressing the previous button to get the last song in the playlist and then opening the queue.
2. To save a web page as an HTML file, right-click on it and choose "Save As". Keep in mind the location where the HTML file was saved.

#### Method 2
Using the provided scraper utilities to open an interactive session.
1. `python scraper.py`
2. Once the browser window is opened you will need to log into Anghami (using the qr code is the easiest option)
3. Navigate to the playlist you would like to extract (as in method 1) and press enter as prompted from the terminal
4. review the output and follow terminal directions to save the playlist.

### Spotify setup
1. Log in or register for a new account at Spotify for Developers - https://developer.spotify.com/dashboard/.
2. Once logged in, go to the dashboard and create a new app. This app will allow you to access the Spotify API.
3. After creating the app, copy the "Client ID" and "Client Secret" values. You may need to click on "Show Client Secret" to reveal it.
4. Click on "Edit Settings" for your app and set the "Redirect URI" to http://127.0.0.1:8080. After authentication, Spotify will reroute users to this website.
5. Go to your Spotify account and copy your account username. This will be used to identify your Spotify account during the migration process.

### Adding the songs on Spotify
1. Open the `config.ini` file and update the client ID, client secret and username values with the data you just acquired. 
2. `python main.py`

## Note
- HTML file path and spotify playlist name can be passed as command line arguments in which case they will override the options specified in the config.ini file. `python main.py -h` for more information.

- If you see a warning when running main.py saying "Possible query problem..". This suggests that when searching for a song on spotify, no exact match was found. You will see the original song extracted from Anghami vs the song which was returned when searching Spotify. 

- If you saved the HTML file in a different location than the script directory, you will need to update the `html_file_path` variable in `config.int` as well.

- Do not forget to update the `playlist_name` variable with the name of the playlist you want to migrate.

## Acknowledgments
The BeautifulSoup library: https://www.crummy.com/software/BeautifulSoup/

The Spotipy library: https://spotipy.readthedocs.io/