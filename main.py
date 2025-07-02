import os

import flask_app
import shutil

from threading import Thread
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from Screens import MainScreen


class TuneTransfer(App):
    """Class that is used to initialise the app"""

    def __init__(self, **kwargs) -> None:
        super(TuneTransfer, self).__init__(**kwargs)

    def build(self) -> ScreenManager:

        # // Create flask app
        Thread(target=flask_app.run_flask_app).start()

        # // Screen manager is used to switch between different screens
        screenmanager = ScreenManager(transition=NoTransition())

        # // Add all screens to screen manager
        screenmanager.add_widget(MainScreen(name='main'))

        screenmanager.current = 'main'

        return screenmanager


if __name__ == "__main__":

    # // clear thumbnails folder if it exists
    try:
        shutil.rmtree('./static/select_pl_screens/thumbnails/sp')
        shutil.rmtree('./static/select_pl_screens/thumbnails/yt')

    except FileNotFoundError:
        pass

    os.makedirs('./static/select_pl_screens/thumbnails/sp')
    os.makedirs('./static/select_pl_screens/thumbnails/yt')

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    TuneTransfer().run()



