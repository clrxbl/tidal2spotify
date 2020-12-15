#!/usr/bin/python3

from secrets import tidal_username, tidal_password, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
import tidalapi
import requests
import sys
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
from time import sleep

def connect_tidal():
    session = tidalapi.Session()
    try:
        session.login(tidal_username, tidal_password)
    except:
        print("Unable to login to Tidal for username=" + tidal_username + ", password=" + tidal_password)
        sys.exit()
    print("Successfully logged into Tidal account " + tidal_username)
    return session

def connect_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(open_browser=False, scope="user-library-read, user-library-modify", client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri="http://localhost/"))
    return sp

def get_tidal_favorite_tracks():
     params = (
           ('limit', 1000),
           ('countryCode', session.country_code),
           ('sessionId', session.session_id),
     )
     response = requests.get('https://api.tidal.com/v1/users/' + str(session.user.id) + '/favorites/tracks', params=params)
     global totalNumberOfItems
     totalNumberOfItems = response.json()['totalNumberOfItems']
     return sorted(response.json()['items'], key=lambda item: datetime.datetime.strptime(item["created"], '%Y-%m-%dT%H:%M:%S.%f%z'))

def print_tidal_favorite_tracks():
    print("Tidal Favorite Trackcount: " + str(totalNumberOfItems))
    print("Tidal Favorite Tracks:")
    for item in favorite_tracks:
        print(item['created'] + ' ' + item['item']['artist']['name'] + ' - ' + item['item']['title'])

def delete_spotify_favorite_tracks():
    offset = 0
    total_favorite_tracks = sp.current_user_saved_tracks(offset=0,limit=1)['total']
    if total_favorite_tracks == 0:
        return
    else:
        delete_favorite_tracks = True
    spotify_favorite_tracks = []
    while delete_favorite_tracks:
        for item in sp.current_user_saved_tracks(offset=offset)['items']:
            spotify_favorite_tracks.append(item['track']['id'])
        offset = offset + 20
        if offset > 20:
            delete_favorite_tracks = False
    print("Deleting favorite Spotify tracks...")
    sp.current_user_saved_tracks_delete(tracks=spotify_favorite_tracks)

def migrate_favorite_tracks():
    for item in favorite_tracks:
        print(item['item']['artist']['name'] + ' - ' + item['item']['title'])
        track = sp.search(item['item']['artist']['name'] + ' - ' + item['item']['title'], limit=1, type='track', market=session.country_code)
        for item in track['tracks']['items']:
            tracklist = []
            tracklist.append(item['id'])
            sp.current_user_saved_tracks_add(tracks=tracklist)
        sleep(1.5)

session = connect_tidal()
favorite_tracks = get_tidal_favorite_tracks()
sp = connect_spotify()

print_tidal_favorite_tracks()
#delete_spotify_favorite_tracks()
migrate_favorite_tracks()
