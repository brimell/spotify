import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Set up Spotify API credentials from environment variables
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8888/callback")
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

def get_playlist_tracks(playlist_id):
    """Fetch all tracks from a playlist."""
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            track = item['track']
            album = track['album']
            release_date = album['release_date']
            track_number = track['track_number']
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'album': album['name'],
                'release_date': release_date,
                'track_number': track_number
            })
        results = sp.next(results) if results['next'] else None
    
    return tracks

def sort_tracks(tracks):
    """Sort tracks by album release date, then by track number."""
    return sorted(tracks, key=lambda x: (x['release_date'], x['album'], x['track_number']))

def create_sorted_playlist(user_id, original_playlist_name, sorted_tracks):
    """Create a new sorted playlist and add tracks to it."""
    new_playlist_name = f"Sorted - {original_playlist_name}"
    new_playlist = sp.user_playlist_create(user_id, new_playlist_name, public=False)
    
    track_ids = [track['id'] for track in sorted_tracks]
    for i in range(0, len(track_ids), 100):  # Spotify allows adding 100 tracks at a time
        sp.playlist_add_items(new_playlist['id'], track_ids[i:i+100])
        time.sleep(1)
    
    return new_playlist['id']

def main():
    playlist_id = input("Enter the Spotify Playlist ID: ")
    user_id = sp.me()['id']
    playlist_info = sp.playlist(playlist_id)
    playlist_name = playlist_info['name']
    
    print("Fetching playlist tracks...")
    tracks = get_playlist_tracks(playlist_id)
    
    print("Sorting tracks...")
    sorted_tracks = sort_tracks(tracks)
    
    print("Creating sorted playlist...")
    new_playlist_id = create_sorted_playlist(user_id, playlist_name, sorted_tracks)
    
    print(f"Sorted playlist created: https://open.spotify.com/playlist/{new_playlist_id}")

if __name__ == "__main__":
    main()