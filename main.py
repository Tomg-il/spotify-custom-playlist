# this projest ask for a year from user, search the popular songs in this year and creates playlist
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse

HOT_100_URL = "https://www.billboard.com/charts/hot-100/"
SPOTIPY_CLIENT_ID = os.environ["SPOTIFY_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIFY_PASS"]
SPOTIPY_REDIRECT_URI = os.environ["SPOTIPY_REDIRECT_URI"]
SPOTIFY_USER_NAME = os.environ["SPOTIFY_USER_NAME"]


def get_date():
    input_date = input("Please insert the requested date DD-MM-YYYY: ")
    try:
        converted_date = datetime.strptime(input_date, '%d-%m-%Y')
    except ValueError:
        print("You inserted wronged value, try again")
        get_date()
    else:
        return converted_date


def get_songs_title(selected_date):
    search_url = HOT_100_URL + str(selected_date)
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    songs_name = soup.select(selector="li h3", class_="c-title", id="title-of-a-story")[:100]
    songs_artist = soup.select(
        selector=" li.o-chart-results-list__item.\/\/.lrv-u-flex-grow-1.lrv-u-flex.lrv-u-flex-direction-column."
                 "lrv-u-justify-content-center.lrv-u-border-b-1.u-border-b-0\@mobile-max.lrv-u"
                 "-border-color-grey-light.lrv-u-padding-l-1\@mobile-max > span", class_="c-label")[:100]
    song_name_list = [name.getText().strip() for name in songs_name]
    song_artist_list = [artist.getText().strip() for artist in songs_artist]
    return song_name_list, song_artist_list


# --------------- create new playlist ---------------------#
def create_playlist(name: str):
    response = sp.user_playlist_create(user=SPOTIFY_USER_NAME, name=name, public=False, collaborative=False,
                                       description="This is automated playlist created for you")
    created_id = response["id"]
    return created_id


def search_title(title_name: str):
    try:
        response = sp.search(q=title_name, type="track", limit=1, market="IL")
    except:
        print("search error")
        return
    else:
        if not response["tracks"]["items"] == []:
            # print(response, response.text)
            # print(f"{response}\n *******************\n")
            song_id = response["tracks"]["items"][0]["id"]
            song_link = response["tracks"]["items"][0]["uri"]
            song_name = response["tracks"]["items"][0]["name"]
            return {"id": song_id, "link": song_link, "name": song_name}
        else:
            print(f"title name was not not found: {title_name}")


# ------------------ ask user for date ---------------------#
# requested_date = get_date()
requested_date: datetime = datetime.strptime("01-01-1984", '%d-%m-%Y')

# --------------  get song tiles from hot-100-utl ---------#
[songs, artists] = get_songs_title(requested_date.date())

# --------------- create access token and spotify object  ---------------------#
scope = "playlist-modify-private"
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
except:
    os.remove(".cache")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# --------------- create new playlist ---------------------#
play_list_name = f"test_playlist{datetime.now().strftime('%H-%M-%S')}"
playlist_id = create_playlist(play_list_name)

# # --------------- search song title ---------------------#
for index in range(0, len(songs)):
    print(f"song name: {songs[index]} index: {index}")
    search_string = f"spotify:track:{songs[index]} artist:{artists[index]}"
    encoded_string = urllib.parse.quote(string=search_string, safe="")
    spotify_song = search_title(encoded_string)
    if spotify_song:
        sp.playlist_add_items(playlist_id=playlist_id, items=[spotify_song["id"]], position=None)
