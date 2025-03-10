from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from User_class import user
from Spotify_class import SpotifyFunctions
from .processing_screen import ProcessingScreen

# // Images used
main_background = './static/main_screen/MainScreen_background.png'
select_playlist_button_image = './static/select_pl_screens/button_select-playlist.png'
empty_button_image = './static/select_pl_screens/button.png'
submit_button_image = './static/select_pl_screens/button_submit.png'


class SelectSpotifyPlScreen(Screen):
    def __init__(self, **kw):
        super(SelectSpotifyPlScreen, self).__init__(**kw)
        self.spotify_client = SpotifyFunctions()

        self.chosen_playlist = None
        self.name_input = None

        # // Page theming
        # self.add_widget(Image(source=main_background, fit_mode='fill'))
        self.add_widget(Button(disabled=True, disabled_color=(49/255, 52/255, 56/255, 1), size=(1, 1)))
        self.add_widget(Label(text="Playlist settings", font_size=96, color=(1, 1, 1, 1), size_hint=(.8, .15),
                              pos_hint={'x': 0.1, 'y': .8}))

        # // Choose name Textinput
        self.add_widget(Label(text="Desired name:", font_size=32, color=(1, 1, 1, 1),
                              size_hint=(.6, .1), pos_hint={'x': .2, 'y': .65}))
        chose_name_text_input = TextInput(multiline=False, size_hint=(.4, .04), pos_hint={'x': .31, 'y': .62})
        chose_name_text_input.bind(text=lambda instance, x: setattr(self, 'name_input', x))
        self.add_widget(chose_name_text_input)

        self.playlists = self.spotify_client.get_user_playlists()
        print(self.playlists)

        # // Scrollview to select a playlist
        self.add_widget(Label(text="Youtube playlist:", font_size=32, color=(1, 1, 1, 1),
                              size_hint=(.6, .1), pos_hint={'x': .2, 'y': .50}))
        scroll_view = ScrollView(do_scroll_y=False, do_scroll_x=True, pos_hint={'x': .2, 'y': .20}, size_hint=(.6, .3))
        playlists_layout = GridLayout(rows=1, spacing=10, size_hint_x=None)

        # // Make sure the height is such that there is something to scroll.
        playlists_layout.bind(minimum_height=playlists_layout.setter('height'))
        playlists_layout.bind(minimum_width=playlists_layout.setter('width'))

        for playlist_name, playlist_id in self.playlists.items():
            pl_button = Button(text=playlist_name, width=600, size_hint_x=None,
                               background_normal=f"./static/select_pl_screens/thumbnails/{playlist_name.replace(' ', '_')}.png")
            pl_button.bind(on_press=self.change_chosen_playlist)
            playlists_layout.add_widget(pl_button)

        scroll_view.add_widget(playlists_layout)
        self.add_widget(scroll_view)

        # // current playlist text
        self.chosen_pl_label = Label(text=f'current choice: {self.chosen_playlist}', font_size=16, color=(1, 1, 1, 1),
                                     size_hint=(.5, .05), pos_hint={'x': .25, 'y': .15})
        self.add_widget(self.chosen_pl_label)

        # // Button to submit playlist info
        submit_button = Button(text="submit", size_hint=(.2, .075), pos_hint={'x': .4, 'y': .05},
                               background_normal=empty_button_image, background_down=empty_button_image)
        submit_button.bind(on_press=self.submit_info)
        self.add_widget(submit_button)

    def change_chosen_playlist(self, instance):
        self.chosen_playlist = instance.text
        self.chosen_pl_label.text = f'current choice: {self.chosen_playlist}'

    def submit_info(self, instance):
        if self.name_input and self.chosen_playlist:

            # // Switch to processing screen
            processing_screen = ProcessingScreen(youtube_client=self.yt_client,
                                                 playlist_name=self.name_input,
                                                 playlist_id_origin=self.playlists[self.chosen_playlist],
                                                 destination=user.destination, name="processing")
            self.manager.add_widget(processing_screen)
            self.manager.current = "processing"
            Clock.schedule_once(processing_screen.create_playlist, .2)