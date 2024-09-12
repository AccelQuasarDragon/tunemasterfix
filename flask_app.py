from flask import Flask, redirect, render_template, Response, request, url_for, session

from User_class import user
from Spotify_class import SpotifyFunctions
from Youtube_class import Youtube

# // Flask app setup
flask_app = Flask(__name__)
flask_app.config['TEMPLATES_AUTO_RELOAD'] = True
flask_app.config['SEND_FILE_MAX_MAX_AGE_DEFAULT'] = 0
flask_app.secret_key = 'TuneTransfer123'

# // Class setups
spotify_client = SpotifyFunctions()


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
        return redirect(url_for('finished_process'))
    else:
        return redirect(url_for('spotify_login'))


@flask_app.route('/splogin')
def spotify_login() -> Response:
    """Login page for spotify"""

    auth_url = spotify_client.spotify_oauth.get_authorize_url()
    return redirect(auth_url)


@flask_app.route('/redirect')
def redirect_page():
    """Redirect page that redirects to get_yt_pl page"""

    print('redirect')

    # // get access token from page link and get user id if needed
    spotify_client.spotify_oauth.get_access_token(request.args['code'])
    spotify_client.get_user_info()

    if user.destination == 'spotify':
        return redirect(url_for('finished_process'))
    else:
        ...


@flask_app.route('/finished_authentication')
def finished_process():
    user.logged_in_spotify = True
    return render_template('finished_login.html')