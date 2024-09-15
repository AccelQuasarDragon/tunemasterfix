from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

from User_class import user
from Youtube_class import Youtube
from .processing_screen import ProcessingScreen

# // Images used
main_background = './static/main_screen/MainScreen_background.png'
select_playlist_button_image = './static/select_pl_screens/button_select-playlist.png'
empty_button_image = './static/select_pl_screens/button.png'
submit_button_image = './static/select_pl_screens/button_submit.png'


class SelectYtPlScreen(Screen):
    def __init__(self, **kw):
        super(SelectYtPlScreen, self).__init__(**kw)
        self.yt_client = Youtube()

        self.chosen_playlist = None
        self.name_input = None

        # // Page theming
        self.add_widget(Image(source=main_background, fit_mode='fill'))
        self.add_widget(Label(text="playlist setup", font_size=96, color=(0, 0, 0, 1),
                              size_hint=(.8, .15), pos_hint={'x': 0.1, 'y': .8}))

        # // Choose name Textinput
        self.add_widget(Label(text="Choose name for Spotify playlist:", font_size=24, color=(0, 0, 0, 1),
                              size_hint=(.6, .1), pos_hint={'x': .2, 'y': .65}))
        chose_name_text_input = TextInput(multiline=False, size_hint=(.4, .05), pos_hint={'x': .3125, 'y': .6})
        chose_name_text_input.bind(text=lambda instance, x: setattr(self, 'name_input', x))
        self.add_widget(chose_name_text_input)

        # Create flow for Google oauth
        if not self.yt_client.flow:
            self.yt_client.create_flow()
        self.playlists = self.yt_client.get_user_playlists()

        # // Creating dropwon menu to pick a playlist
        dropdown = DropDown()
        for playlist in self.playlists.keys():
            btn = Button(text=playlist, size_hint_y=None, height=100, width=Window.size[0] // 3,
                         background_normal=empty_button_image, background_down=empty_button_image)
            btn.bind(on_release=lambda instance: dropdown.select(instance.text))
            dropdown.add_widget(btn)

        # // Main button that opens dropwown
        self.open_dropdown_button = Button(size_hint=(.3, .125), pos_hint={'x': .35, 'y': .45},
                                           background_normal=select_playlist_button_image,
                                           background_down=select_playlist_button_image)
        self.open_dropdown_button.bind(on_release=dropdown.open)

        dropdown.bind(on_select=lambda instance, x: setattr(self, 'chosen_playlist', x))
        self.add_widget(self.open_dropdown_button)

        # // Button to submit playlist info
        submit_button = Button(size_hint=(.2, .1), pos_hint={'x': .4, 'y': .2},
                               background_normal=submit_button_image, background_down=submit_button_image)
        submit_button.bind(on_press=self.submit_info)
        self.add_widget(submit_button)

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
