import flask
from flask import Flask, redirect, render_template, Response, request, url_for
import google_auth_oauthlib.flow
import googleapiclient.discovery

from Spotify_class import SpotifyFunctions
from Youtube_class import Youtube

# // Flask app setup
flask_app = Flask(__name__)
flask_app.config['TEMPLATES_AUTO_RELOAD'] = True
flask_app.config['SEND_FILE_MAX_MAX_AGE_DEFAULT'] = 0
flask_app.secret_key = 'TuneTransfer123'

# // Class setups
spotify_client = SpotifyFunctions()
youtube_client = Youtube()

# // Variables
credentials = None
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/youtube',
                 'https://www.googleapis.com/auth/youtubepartner',
                 'https://www.googleapis.com/auth/youtube.force-ssl']


# // User login process:
# To Youtube:
#   -
#   -
#   -
#   -
#   -
#   -

# To Spotify
#   -
#   -
#   -
#   -
#   -
#   -

def run_flask_app():
    return flask_app.run(host='127.0.0.1', port=5000)


@flask_app.route("/")
def main():
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


@flask_app.route('/toyoutube')
def to_youtube() -> Response:
    """Redirection page entered by hitting the spotify -> youtube button"""

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

    # // get access token from page link and get user id if needed
    spotify_client.spotify_oauth.get_access_token(request.args['code'])
    spotify_client.get_user_info()

    return redirect(url_for('youtube_login_flow'))


@flask_app.route('/ytlogin-flow')
def youtube_login_flow() -> Response:
    """Login page for youtube's flow, used to set up an Oath connection"""

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', GOOGLE_SCOPES, redirect_uri='http://127.0.0.1:5000/ytlogin-response')
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true',
                                                      prompt='consent')
    flask.session['state'] = state
    return redirect(authorization_url)


@flask_app.route('/ytlogin-response')
def youtube_login_oath_response() -> Response:
    """Login page for youtube's/flow response to oath-request"""
    global credentials

    state = flask.session['state']
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', GOOGLE_SCOPES, state=state)
    flow.redirect_uri = flask.url_for('youtube_login_oath_response', _external=True)
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'granted_scopes': credentials.granted_scopes}

    youtube_client.youtube_build = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

    return redirect(url_for('finished_process'))


@flask_app.route('/finished_authorization')
def finished_process():
    youtube_client.logged_in = True
    return render_template('finished_login.html')