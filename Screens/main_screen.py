from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


class MainScreen(Screen):
    def __init__(self, **kw):
        super(MainScreen, self).__init__(**kw)
        self.add_widget(MainScreenWidgets())


class MainScreenWidgets(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Button(text='hello'))