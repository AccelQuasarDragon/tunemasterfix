import jaro
import spotipy

from data import api_keys
from flask import session
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


# Spotify variables
SPOTIFY_CLIENT_ID = api_keys["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = api_keys["SPOTIFY_CLIENT_SECRET"]
scopes = ['playlist-read-collaborative', 'user-read-private', 'playlist-modify-private',
          'playlist-read-private']

# Variables
features_to_remove = ["[feat", "(feat", "feat", "[ft", "(ft", "ft", "[with", "(with", "with"]
types_of_underscores: list = ['-', '-', '–', '-']


class SpotifyFunctions:
    """Class that contains all functions that use spotify api"""

    def __init__(self):
        self.cache_handler = FlaskSessionCacheHandler(session)
        self.spotify_oauth: spotipy.SpotifyOAuth = self.oauth_setup()
        self.sp: spotipy.Spotify = Spotify(auth_manager=self.spotify_oauth)
        self.user_id = None

    def oauth_setup(self):

        # handles spotify oauth
        return SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri='http://127.0.0.1:5000/redirect',
            scope=scopes,
            show_dialog=True
        )

    def check_token(self) -> bool:
        """Check if user is logged into spotify"""

        # check if the user has a valid access token and thus is logged in
        if not self.spotify_oauth.validate_token(self.cache_handler.get_cached_token()):
            return False
        else:
            return True

    def get_user_info(self) -> None:
        """Use Spotify client to get current user info"""

        self.user_id = self.sp.current_user()['id']

    def get_user_playlists(self) -> dict:
        """Use Spotify client to aqcuire a list of the user's Spotify playlists"""

        playlists = {}

        playlist_result = self.sp.current_user_playlists()

        # // Extract playlist titles and ids
        for playlist in playlist_result['items']:
            print(playlist)
            playlist_name = playlist['name']
            playlist_id = playlist['id']
            playlists[playlist_name] = playlist_id

            download_playlist_thumbnail()

        print(playlists)
        return playlists

    def get_playlist_items(self, playlist_id) -> list[str]:
        """Function that gets song names from a Spotify playlist"""

        song_names = []

        playlist_items = self.sp.playlist_items(playlist_id)

        total_songs = len(playlist_items['items'])

        while True:
            for index in range(total_songs):
                artist = playlist_items['items'][index]['track']['artists'][0]['name']
                raw_song_name = playlist_items['items'][index]['track']['name']
                full_song_name = f'{artist} - {raw_song_name} - official audio'
                song_names.append(full_song_name)

            if playlist_items['next']:
                playlist_items = self.sp.next(playlist_items)
            else:
                break

        return song_names

    def create_spotify_playlist(self, playlist_name) -> str:
        """Use Spotify client to create a new playlist on the current user's account and return its id for
        future use"""

        new_playlist = self.sp.user_playlist_create(user=self.user_id, name=playlist_name,
                                                    public=False, collaborative=False)
        return new_playlist['id']

    def add_song_to_playlist(self, playlist_id: str, song_name: str) -> None:
        """Add a song to a previously created playlist"""

        results = []
        highest_similarity = 0
        current_uri = None

        # // Split the search into two parts, one with features and 1 without
        song_name_no_features = remove_features(song_name.upper())

        spotify_result_with_features = self.sp.search(q=song_name.lower(), limit=5, type=['track'])
        spotify_result_no_features = self.sp.search(q=song_name_no_features, limit=5, type=["track"])

        # // Gather results from both searches
        for i in range(5):
            # // Group 1: Featuring the song name with featured artists, both normal and reversed,
            # for youtube videos that have a reversed title format
            # step 1: gather artist and title data from the spotify search
            song_artist_with_features = spotify_result_with_features['tracks']['items'][i]['artists'][0]['name']
            song_title_with_features = spotify_result_with_features['tracks']['items'][i]['name']
            song_uri_with_features = spotify_result_with_features['tracks']['items'][i]['uri']

            # step 2: assamble the full name of the song, now including the main artist, send this to the results
            title_with_features_normal = f'{song_artist_with_features} - {song_title_with_features}'
            title_with_features_reversed = f'{song_title_with_features} - {song_artist_with_features}'

            results.append((title_with_features_normal, title_with_features_reversed, song_uri_with_features))

            # // Group 2: Featuring the song name without featured artists, both normal and reversed,
            # for youtube videos that have a reversed title format
            # step 1: gather artist and title data from the spotify search
            song_artist_no_features = spotify_result_no_features['tracks']['items'][i]['artists'][0]['name']
            song_title_no_features = spotify_result_no_features['tracks']['items'][i]['name']
            song_uri_no_features = spotify_result_no_features['tracks']['items'][i]['uri']

            # step 2: assamble the full name of the song, now including the main artist, send this to the results
            title_no_features_normal = f'{song_artist_no_features} - {song_title_no_features}'
            title_no_features_reversed = f'{song_title_no_features} - {song_artist_no_features}'

            results.append((title_no_features_normal, title_no_features_reversed, song_uri_no_features))

        # // Go through every result and compare with both the feature and no feature song title
        for result in results:
            song_title_normal, song_title_reversed, song_uri = result

            # // Group 1: song titles with the features, both normal and reversed
            similarity_with_features_normal_title = jaro.jaro_metric(song_title_normal.upper(), song_name.upper())
            similarity_with_features_reversed_title = jaro.jaro_metric(song_title_reversed.upper(), song_name.upper())

            # // Group 2: song titles without the features, both normal and reversed
            similarity_no_features_normal_title = jaro.jaro_metric(song_title_normal.upper(), song_name_no_features.upper())
            similarity_no_features_reversed_title = jaro.jaro_metric(song_title_reversed.upper(), song_name_no_features.upper())

            # // Check if any of the calculated similarities are a new highest score, along the way,
            # filter out any unwanted versions
            best_match_score = max(similarity_with_features_normal_title, similarity_with_features_reversed_title,
                                   similarity_no_features_normal_title, similarity_no_features_reversed_title)

            if best_match_score > highest_similarity:
                if "REMIX" in song_title_normal.upper() and "REMIX" not in song_name.upper():
                    pass
                elif "PARTY" in song_title_normal.upper() and "PARTY" not in song_name.upper():
                    pass
                elif "KARAOKE" in song_title_normal.upper() and "KARAOKE" not in song_name.upper():
                    pass
                else:
                    highest_similarity = best_match_score
                    current_uri = song_uri

        # // Finally, add the final choice to the playlist
        self.sp.playlist_add_items(playlist_id=playlist_id, items=[current_uri])


def remove_features(song_title: str) -> str:
    """Function that removes features from a song title,
     spotify often doesn't mention features in the title even though this is a thing on youtube"""

    # // Split the song title in two parts, one artist, one song name
    name_part_1 = None
    name_part_2 = None

    for underscore in types_of_underscores:
        try:
            name_part_1, name_part_2 = song_title.split(underscore)
            break
        except ValueError:
            pass

    # / If the video title contains an underscore
    if name_part_1 and name_part_2:

        # // Remove features from the song title for better results from the spotify api
        for tag in features_to_remove:
            try:
                name_part_1, _ = name_part_1.split(tag.upper())
            except ValueError:
                pass

            try:
                name_part_2, _ = name_part_2.split(tag.upper())
            except ValueError:
                pass

        # // Put song parts back together and remove unwanted spaces
        song_title = f"{name_part_1} - {name_part_2}"

        for i in range(2, 6):
            song_title = song_title.replace(' ' * i, ' ')
    else:
        pass

    return song_title.lower()


def download_playlist_thumbnail():
    ...
