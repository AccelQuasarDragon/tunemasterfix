import time
from functools import partial

from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.progressbar import ProgressBar

from flask_app import spotify_client

# // Images used
main_background = './static/main_screen/MainScreen_background.png'


class ProcessingScreen(Screen):
    def __init__(self, youtube_client, playlist_name, playlist_id_origin, destination, **kw):
        super().__init__(**kw)

        self.yt_client = youtube_client
        self.destination = destination
        self.playlist_name = playlist_name
        self.playlist_id_origin = playlist_id_origin
        self.playlist_id = ''
        self.current_song = 0
        self.song_count = 0
        self.songs = []

        # // Page theming
        self.add_widget(Image(source=main_background, fit_mode='fill'))
        self.add_widget(Label(text="processing your request", font_size=64, color=(0, 0, 0, 1),
                              size_hint=(.3, .05), pos_hint={'x': .35, 'y': .8}))

        # // Progress bar
        self.pb = ProgressBar(max=100, value=0,
                              size_hint=(.6, .15), pos_hint={'x': .2, 'y': .5})
        self.add_widget(self.pb)

    def create_playlist(self, dt: int | float) -> None:
        """Main function in control of creating and filling a new playlist"""

        if self.destination == 'spotify':
            self.songs = self.yt_client.get_playlist_items(self.playlist_id_origin)
            self.song_count = len(self.songs)
            self.pb.max = self.song_count * 2
            self.pb.value = self.song_count

            # // Use spotipy to create a new playlist
            self.playlist_id = spotify_client.create_spotify_playlist(self.playlist_name)
            Clock.schedule_once(partial(self.update_spotify_playlist, 0), 0)

    def update_spotify_playlist(self, iteration: int, dt: int | float) -> None:
        """Add a new song to the spotify playlist that was created earlier"""

        spotify_client.add_song_to_playlist(self.playlist_id, self.songs[iteration])
        Clock.schedule_once(partial(self.update_progress_bar, iteration + 1), 0)

    def update_progress_bar(self, iteration: int, dt: int | float) -> None:
        """Update the progress bar on screen to keep the user updated about the progress"""

        self.pb.value += 1
        if iteration != self.song_count:
            Clock.schedule_once(partial(self.update_spotify_playlist, iteration), 0)


            


