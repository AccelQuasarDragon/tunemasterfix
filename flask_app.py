import os

from flask import Flask, redirect, render_template, Response, request, url_for

from User_class import user
from Spotify_class import SpotifyFunctions
from Youtube_class import Youtube

# // Flask app setup
flask_app = Flask(__name__)
flask_app.config['SERVER_NAME'] = '127.0.0.1:5000'
flask_app.config['SESSION_COOKIE_NAME'] = 'Cookies'
flask_app.config['TEMPLATES_AUTO_RELOAD'] = True
flask_app.config['SEND_FILE_MAX_MAX_AGE_DEFAULT'] = 0
flask_app.secret_key = 'TuneTransfer123'

# // Class setups
spotify_client = SpotifyFunctions()
youtube_client = Youtube(flask_app)


def run_flask_app():
    return flask_app.run(host='127.0.0.1', port=5000)


def switch_routes(route_name):
    return redirect(url_for(f'{route_name}'))


@flask_app.route("/")
def hello():
    return render_template('main.html')


@flask_app.route('/tospotify')
def to_spotify() -> Response:
    """Redirection page entered by hitting the yt -> spotify button"""

    # check if user is logged in, if yes get their id and otherwise redirect them to login
    if spotify_client.check_token():
        spotify_client.get_user_info()
        return redirect(url_for('get_yt_playlist'))
    else:
        return redirect(url_for('spotify_login'))


@flask_app.route('/splogin')
def spotify_login() -> Response:
    """Login page for spotify"""

    auth_url = spotify_client.spotify_oauth.get_authorize_url()
    return redirect(auth_url)


@flask_app.route('/redirect')
def redirect_page() -> Response | None:
    """Redirect page that redirects to get_yt_pl page"""

    print('redirect')

    # // get access token from page link and get user id if needed
    spotify_client.spotify_oauth.get_access_token(request.args['code'])
    spotify_client.get_user_info()

    if user.destination == 'spotify':
        print("1")
        return redirect(url_for('get_yt_playlist'))
    else:
        print('2')
        ...


@flask_app.route('/get_youtube_playlist', methods=['GET', 'POST'])
def get_yt_playlist() -> Response | str:
    """Page that gets an id of and song names in a yt playlist and checks its validity"""

    print('get_yt_pl')

    # check if user is logged in
    if not spotify_client.check_token():
        return redirect(url_for('spotify_login'))

    return render_template('youtube_playlist_select_page.html')

    # # Create flow for Google oauth
    # if not Youtube.flow:
    #     Youtube.create_flow()
    #
    # while True:
    #
    #     # wait until user clicks submit button
    #     if request.method == 'POST':
    #         id_input = request.form['yt_playlist_id']
    #         wanted_playlist_name = request.form['sp_playlist_wanted_name']
    #
    #         # check if playlist is valid and if yes get the items in the playlist
    #         if Youtube.validate_playlist(id_input):
    #             song_names = Youtube.get_playlist_items(id_input)
    #             break
    #         else:
    #             return render_template('youtube_playlist_select_page.html')
    #
    #     else:
    #         return render_template('youtube_playlist_select_page.html')
    #
    # spotify_client.create_spotify_playlist(wanted_playlist_name, song_names)
    #
    # return render_template('process_done.html')