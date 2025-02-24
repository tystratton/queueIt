import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()
# Define the scope. Here we're requesting permission to read the currently playing track.
scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# Create the Spotify client with OAuth credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),             # Replace with your client ID
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),     # Replace with your client secret
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),       # Replace with your redirect URI
    scope=scope
))

# Fetch the currently playing track
current_playback = sp.current_playback()

if current_playback and current_playback['is_playing']:
    track = current_playback['item']
    track_name = track['name']
    artists = ", ".join([artist['name'] for artist in track['artists']])
    print(f"Now playing: {track_name} by {artists}")
else:
    print("No track is currently playing.")
