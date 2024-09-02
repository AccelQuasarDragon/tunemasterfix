from threading import Thread

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition

from flask_app import FlaskApp
from Screens import MainScreen


class TuneTransfer(App):
    """Class that is used to initialise the app"""

    def __init__(self, **kwargs) -> None:
        super(TuneTransfer, self).__init__(**kwargs)

    def build(self) -> ScreenManager:

        # // Create flask app
        Thread(target=FlaskApp().create_flask_app_routes).start()

        # // Screen manager is used to switch between different screens
        screenmanager = ScreenManager(transition=NoTransition())

        # // Add all screens to screen manager
        screenmanager.add_widget(MainScreen(name='main'))

        screenmanager.current = 'main'

        return screenmanager


if __name__ == "__main__":
    TuneTransfer().run()



