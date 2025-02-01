import configparser
import argparse
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from thefuzz import fuzz
from tqdm import tqdm
from scraper import extract_songs_and_artists

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger()

# todo break down this file into multiple components maybe
# todo append to a playlist


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Script to migrate Anghami playlists to Spotify.")

    # Anghami configuration
    parser.add_argument('--anghami_html', type=str,
                        help="Path to the HTML file for Anghami.")
    parser.add_argument('--spotify_playlist', type=str,
                        help="Name of the generated playlist.")
    return parser

# Function to load the details from the configuration file


def load_details() -> dict:
    config = configparser.ConfigParser()
    config.read('config.ini')
    details = {
        "html_file_path": config.get('Anghami', 'html_file_path'),
        "client_id": config.get('Spotify', 'client_id'),
        "client_secret": config.get('Spotify', 'client_secret'),
        "redirect_url": config.get('Spotify', 'redirect_url'),
        "username": config.get('Spotify', 'username'),
        "spotify_playlist_name": config.get('Spotify', 'playlist_name'),
        "save_to_text": config.getboolean('General', 'save_to_text'),
        "txt_save_path": config.get('General', 'txt_save_path'),
        "txt_song_artist_separator": config.get('General', 'txt_song_artist_separator'),
    }

    # override any argument which was specified via the command line
    parser = create_parser()
    args = parser.parse_args()
    if args.anghami_html:
        details['html_file_path'] = args.anghami_html
    if args.spotify_playlist:
        details['spotify_playlist_name'] = args.spotify_playlist

    return details


def read_html_file(html_file_path):
    with open(html_file_path, encoding="utf8") as f:
        content = f.read()
    return content


def save_playlist_to_text(songs, artists, txt_save_path, txt_song_artist_separator):
    with open(txt_save_path, 'w', encoding="utf8") as fp:
        for song, artist in zip(songs, artists):
            fp.write(f"{song}{txt_song_artist_separator}{artist}\n")


def authenticate_spotify(client_id, client_secret, redirect_url, username):
    scope = 'playlist-modify-public'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_url,
                                                   scope=scope,
                                                   username=username))
    return sp


def create_spotify_playlist(sp, username, spotify_playlist_name):
    playlist = sp.user_playlist_create(user=username, name=spotify_playlist_name, public=True,
                                       description="Imported from Anghami")
    return playlist['id']


def check_search_quality(anghamiSong: str, anghamiArtist: str,
                          spotifySong: str, spotifyArtist: str):
    """Check search quality by calculating the difference between the name of the song found
    on Spotify vs the original song which was requested. Warn user if the difference exceeds
    a certain threshold.

    Args:
        anghamiSong (str): Anghami song name
        anghamiArtist (str): Anghami artist name
        spotifySong (str): Spotify song name
        spotifyArtist (str): Spotify artist name
    """
    anghamiString = f"{anghamiSong} {anghamiArtist}"
    spotifyString = f"{spotifySong} {spotifyArtist}"
    ratio = fuzz.token_sort_ratio(anghamiString, spotifyString)
    # this threshold was chosen based on empirical testing. perhaps it could be further optimized?
    if ratio < 85:
        logger.warning(
            f"Possible query problem. Requested {anghamiString.strip()}. Best match on Spotify {spotifyString}")


def search_and_add_tracks(sp, playlist_id, songs, artists, username):
    not_found = []
    for song, artist in tqdm(zip(songs, artists), total=len(songs), bar_format="{l_bar}{bar}{r_bar}", colour='green'):
        try:
            res = sp.search(q=f"{song} {artist}", type='track', limit=1)
            if len(res['tracks']['items']) > 0:
                best_match = res['tracks']['items'][0]
                check_search_quality(song, artist, best_match['name'], " ".join(
                    artist['name'] for artist in best_match['artists']))
                uri = best_match['uri']
                sp.user_playlist_add_tracks(
                    user=username, playlist_id=playlist_id, tracks=[uri])
            else:
                not_found.append(f"{song} {artist}")
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify Error: {str(e)}")
            not_found.append(f"{song} {artist}")

    return not_found


def main():
    # Load details from configuration file
    details = load_details()

    # Read the HTML file
    content = read_html_file(details['html_file_path'])

    # Extract songs and artists from the HTML
    songs, artists = extract_songs_and_artists(content)

    # Check if the number of songs matches the number of artists
    if len(songs) != len(artists):
        logger.error("Error: Number of songs and artists do not match.")
        return

    # Print the playlist details
    logger.info("\nPlaylist Details:")
    for song, artist in zip(songs, artists):
        logger.info(f"{song} {details['txt_song_artist_separator']} {artist}")

    # Save the playlist to a text file
    if details['save_to_text']:
        save_playlist_to_text(
            songs, artists, details['txt_save_path'], details['txt_song_artist_separator'])
        logger.info("Playlist saved to text file.")

    # Authenticate and create a new playlist on Spotify
    sp = authenticate_spotify(
        details['client_id'], details['client_secret'], details['redirect_url'], details['username'])
    playlist_id = create_spotify_playlist(
        sp, details['username'], details['spotify_playlist_name'])

    # Search and add tracks to the Spotify playlist
    logger.info("Importing playlist to Spotify...")
    not_found = search_and_add_tracks(
        sp, playlist_id, songs, artists, details['username'])

    logger.info("Playlist import completed.")

    # Print the not found songs
    if len(not_found) > 0:
        logger.info("\nThe following songs could not be found on Spotify:")
        for song in not_found:
            logger.info(song)


if __name__ == '__main__':
    main()
