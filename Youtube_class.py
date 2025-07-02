import re
import requests

from data import api_keys
from youtube_search import YoutubeSearch

# Google/Youtube setup
GOOGLE_CLIENT_ID = api_keys['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = api_keys['GOOGLE_CLIENT_SECRET']
CLIENT_FILE = 'client_secrets.json'
REDIRECT_URI = 'http://127.0.0.1:5000/ytplaylistselect'
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/youtube',
                 'https://www.googleapis.com/auth/youtubepartner',
                 'https://www.googleapis.com/auth/youtube.force-ssl']
YT_DEV_KEY = None

# Variables
loose_terms_to_remove = ['VEVO', '- Topic', '4K Upgrade', '- Radio Edit', "HD",
                         "Explicit", ' - lyrics video', ' - lyric video', "audio"]


class Youtube:
    """Class that contains all functions using the Youtube API"""

    def __init__(self):
        self.logged_in = False
        self.youtube_build = None

    def get_playlist_items(self, playlist_id) -> list:
        """Function that uses yt api to get song names from a playlist"""

        next_page_token: str | None = None
        song_names: list = []

        while True:

            # // Check if a next page with more songs exist
            if next_page_token:
                playlist_request = self.youtube_build.playlistItems().list(part='snippet',
                                                                           playlistId=playlist_id,
                                                                           pageToken=next_page_token,
                                                                           maxResults=50)
            else:
                playlist_request = self.youtube_build.playlistItems().list(part='snippet',
                                                                           playlistId=playlist_id,
                                                                           maxResults=50)

            playlist_response = playlist_request.execute()
            items_on_page = len(playlist_response['items'])

            # Go through every song and get its name and artist
            for index in range(items_on_page):
                yt_video_id: str = playlist_response['items'][index]['snippet']['resourceId']['videoId']

                try:
                    song_name_request = self.youtube_build.videos().list(part='snippet', id=yt_video_id)
                    # time.sleep(0.1)
                    song_name_response = song_name_request.execute()
                    song_name = song_name_response['items'][0]['snippet']['title']
                    song_artist = song_name_response['items'][0]['snippet']['channelTitle']

                    song_name = optimize_song_name(song_name, song_artist)
                    song_names.append(song_name)

                except IndexError:
                    pass

            # check if there is a next page with songs and end function if not
            try:
                next_page_token: str = playlist_response['nextPageToken']
            except KeyError:
                break

        return song_names

    def get_user_playlists(self) -> dict:
        """Function that collects a dict of the user's playlist for use in the dropdown menu"""

        playlists = {}

        # // Get playlists from youtube api
        playlists_raw_reponse = self.youtube_build.playlists().list(part="snippet", mine=True).execute()

        # // Extract playlist titles and ids from raw response
        for playlist in playlists_raw_reponse['items']:
            playlist_name = playlist["snippet"]["title"]
            playlist_id = playlist["id"]
            playlists[playlist_name] = playlist_id

            download_playlist_thumbnail(playlist)

        return playlists

    def create_yt_playlist(self, playlist_name):
        """Function that uses yt api to create a new playlist and returns its id"""

        # Create a new playlist and get its id
        new_pl = self.youtube_build.playlists().insert(part="snippet,contentDetails",
                                                       body={"snippet": {"title": playlist_name}}).execute()
        return new_pl['id']

    def add_song_to_playlist(self, playlist_id, song_name):
        """Insert a song into the playlist created above"""

        song_id = get_song_id(song_name)
        self.youtube_build.playlistItems().insert(part='snippet,contentDetails', body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": song_id
                }
            }
        }).execute()


def get_song_id(song_name: str) -> str:
    """Function that uses youtube_search to get song names, bypassing quota use"""

    raw_song_names = YoutubeSearch(song_name, max_results=5).to_dict()
    song_id = raw_song_names[0]['id']

    return song_id


def optimize_song_name(song_name: str, channel_title: str) -> str:
    """Optimize a song name to include both title and artist to get optimal results from spotify api"""

    song_name = song_name.upper()

    # // Remove unwanted brackets
    matches_with_brackets = re.findall("[[({].*?[])}]", song_name)
    for match in matches_with_brackets:
        if not any(x.upper() in match.upper() for x in ['feat', 'ft', 'remix', 'edit']):
            song_name = song_name.replace(match.upper(), '')

    # // remove loose unwanted terms from song name, do this twice to avoid nested terms
    for i in range(2):
        for term in loose_terms_to_remove:
            song_name = song_name.replace(f' {term.upper()}', '')
            song_name = song_name.replace(f'{term.upper()} ', '')
            song_name = song_name.replace(term.upper(), '')

        for x in range(2, 6):
            song_name = song_name.replace(' ' * x, ' ')

    return song_name


def download_playlist_thumbnail(playlist) -> None:
    """Downloads the images of the user's playlists to aid the playlist choice"""

    playlist_name = playlist["snippet"]["title"]

    # // Download the best possible thumbnail image
    for res in ['maxres', 'standard']:
        try:
            thumbnail_url = playlist["snippet"]["thumbnails"][res]['url']
            r = requests.get(thumbnail_url, stream=True, verify=False)

            with open(f"./static/select_pl_screens/thumbnails/yt/{playlist_name.replace(' ', '_')}.png", 'wb') as f:
                f.write(r.content)
                return

        except KeyError:
            continue

    # // set not available image
    else:
        with open(f"./static/select_pl_screens/thumbnails/yt/{playlist_name.replace(' ', '_')}.png", 'wb') as f:
            r = requests.get("https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.istockphoto.com%2Fphotos%2Fimage-not-found&psig=AOvVaw3owZbGT0qxCkiZwkuNZnOk&ust=1744038498346000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCNDxju3Xw4wDFQAAAAAdAAAAABAE", stream=True, verify=False)
            f.write(r.content)
            return
