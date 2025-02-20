import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, jsonify, render_template


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Your Spotify App Credentials (Stored Securely on the Backend)
SPOTIPY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Define the scope (What permissions are requested)
SCOPE = "user-read-currently-playing user-read-playback-state"

# Create the Spotify OAuth manager
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
)


@app.route('/')
def login():
    """ Redirect users to Spotify authentication """
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """ Handle Spotify OAuth Callback """
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info
    return redirect('/current-track')


@app.route('/current-track')
def get_current_track():
    """ Fetch the current track and return JSON response """
    token_info = session.get("token_info", None)

    if not token_info:
        return jsonify({"error": "Not authenticated"}), 401

    sp = spotipy.Spotify(auth=token_info["access_token"])
    current_playback = sp.current_playback()

    if current_playback and current_playback['is_playing']:
        track = current_playback['item']
        track_name = track['name']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        return jsonify({"track": track_name, "artists": artists})
    
    return jsonify({"message": "No track currently playing"})

@app.route('/current-track-widget')
def current_track_widget():
    return render_template('index.html')

@app.route('/auth')
def auth():
    """Handle Spotify OAuth Callback"""
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    
    session["token_info"] = token_info
    return redirect('/current-track')  # Redirect to current-track after successful auth


if __name__ == "__main__":
    app.run(debug=True, port=5000)
