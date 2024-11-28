import webbrowser

from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen

from User_class import user
from .select_youtube_pl_screen import SelectYtPlScreen

# // Images used
main_background = './static/main_screen/MainScreen_background.png'
text_logo = './static/main_screen/TuneTransfer_new_text.png'
to_sp_button_image = './static/main_screen/button_transfer-to-spotify.png'
to_yt_button_image = './static/main_screen/button_transfer-to-youtube.png'


class MainScreen(Screen):
    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)

        self.add_widget(Image(source=main_background, fit_mode='fill'))
        self.add_widget(Image(source=text_logo, pos_hint={'x': 0, 'y': .3}))

        to_sp_button = Button(size_hint=(.4, .075), pos_hint={'x': .3, 'y': .6},
                              background_normal=to_sp_button_image, background_down=to_sp_button_image)
        to_sp_button.bind(on_press=self.go_to_sp)

        to_yt_button = Button(size_hint=(.4, .075), pos_hint={'x': .3, 'y': .45},
                              background_normal=to_yt_button_image, background_down=to_yt_button_image)
        to_yt_button.bind(on_press=self.go_to_yt)

        self.add_widget(to_yt_button)
        self.add_widget(to_sp_button)

    def go_to_yt(self, instance):
        ...

    def go_to_sp(self, instance):
        user.destination = 'spotify'
        webbrowser.open("http://127.0.0.1:5000/tospotify")

        while not user.logged_in_spotify:
            pass

        self.manager.add_widget(SelectYtPlScreen(name='select_yt_pl'))
        self.manager.current = 'select_yt_pl'
