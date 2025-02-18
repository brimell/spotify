import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Set up Spotify API credentials from environment variables
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    raise ValueError("Missing Spotify API credentials. Ensure SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET are set.")

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
            if track:  # Ensure track exists
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

def update_sorted_playlist(playlist_id, sorted_tracks):
    """Update an existing playlist with sorted tracks."""
    track_ids = [track['id'] for track in sorted_tracks]
    sp.playlist_replace_items(playlist_id, track_ids[:100])
    for i in range(100, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i+100])
        time.sleep(1)
    return playlist_id

def get_user_playlists():
    """Fetch all user playlists and allow user selection."""
    playlists = sp.current_user_playlists()
    playlist_dict = {}
    print("Your playlists:")
    for idx, playlist in enumerate(playlists['items']):
        print(f"{idx + 1}. {playlist['name']} ({playlist['id']})")
        playlist_dict[str(idx + 1)] = playlist['id']
    
    selected_indices = input("Enter the numbers of the playlists you want to sort (comma-separated): ").split(',')
    return [playlist_dict[idx.strip()] for idx in selected_indices if idx.strip() in playlist_dict]

def main():
    user_id = sp.me()['id']
    
    print("Fetching your playlists...")
    playlist_ids = get_user_playlists()
    
    for playlist_id in playlist_ids:
        playlist_info = sp.playlist(playlist_id)
        playlist_name = playlist_info['name']
        
        print(f"Fetching tracks for {playlist_name}...")
        tracks = get_playlist_tracks(playlist_id)
        
        if not tracks:
            print(f"No tracks found in {playlist_name}.")
            continue
        
        print(f"Sorting tracks for {playlist_name}...")
        sorted_tracks = sort_tracks(tracks)
        
        print(f"Updating sorted playlist: {playlist_name}...")
        update_sorted_playlist(playlist_id, sorted_tracks)
        
        print(f"Updated playlist: https://open.spotify.com/playlist/{playlist_id}")

if __name__ == "__main__":
    main()