import webbrowser

from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from User_class import user
from .select_youtube_pl_screen import SelectYtPlScreen
from .select_sp_pl_screen import SelectSpotifyPlScreen

# // Images used
main_background = './static/main_screen/MainScreen_background.png'
new_logo = './static/TuneTransferLogo.png'
tunetransfer_text = '.static/main_screen/TuneTransfer-white_text.png'
to_sp_button_image = './static/main_screen/button_transfer-to-spotify.png'
to_yt_button_image = './static/main_screen/button_transfer-to-youtube.png'


class MainScreen(Screen):
    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        self.add_widget(Button(disabled=True, disabled_color=(49 / 255, 52 / 255, 56 / 255, 1), size=(1, 1)))
        self.add_widget(Image(source=new_logo, pos_hint={'x': .4, 'y': .7}, size_hint=(.2, .2)))
        self.add_widget(Label(text="TuneTransfer", color=(1, 1, 1, 1), font_size=64,
                              pos_hint={'x': .4075, 'y': .56}, size_hint=(.2, .2)))

        to_sp_button = Button(size_hint=(.5, .075), pos_hint={'x': .25, 'y': .5},
                              background_normal=to_sp_button_image, background_down=to_sp_button_image)
        to_sp_button.bind(on_press=self.go_to_sp)

        to_yt_button = Button(size_hint=(.5, .075), pos_hint={'x': .25, 'y': .35},
                              background_normal=to_yt_button_image, background_down=to_yt_button_image)
        to_yt_button.bind(on_press=self.go_to_yt)

        self.add_widget(to_yt_button)
        self.add_widget(to_sp_button)

    def go_to_yt(self, instance):
        user.destination = 'youtube'
        webbrowser.open("http://127.0.0.1:5000/toyoutube")

        while not user.logged_in_spotify:
            pass

        self.manager.add_widget(SelectSpotifyPlScreen(name='select_sp_pl'))
        self.manager.current = 'select_sp_pl'

    def go_to_sp(self, instance):
        user.destination = 'spotify'
        webbrowser.open("http://127.0.0.1:5000/tospotify")

        while not user.logged_in_spotify:
            pass

        self.manager.add_widget(SelectYtPlScreen(name='select_yt_pl'))
        self.manager.current = 'select_yt_pl'
