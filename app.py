from flask import Flask, render_template, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import time
from palettable.cubehelix import Cubehelix
import json
from random import randint
from statistics import mode
from settings import appKey, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


app= Flask(__name__, template_folder='templates')
app.secret_key= appKey
app.config['SESSION_COOKIE_NAME']= 'Tanyas Cookie'
TOKEN_INFO= 'token_info'
cache_handler= FlaskSessionCacheHandler(session)


def create_spotify_oauth():
    return SpotifyOAuth(
         client_id= SPOTIPY_CLIENT_ID,
         client_secret= SPOTIPY_CLIENT_SECRET,
         redirect_uri='http://127.0.0.1:5000/toptracks',
         scope= 'user-top-read',
         cache_handler=cache_handler,
         show_dialog=True
    )

         

@app.route("/")
def index():
    sp_oauth= create_spotify_oauth()
    auth_url= sp_oauth.get_authorize_url()
    return render_template('index.html', auth_url=auth_url)


@app.route('/toptracks')
def redirector():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
        session[TOKEN_INFO] = token_info
    return redirect('/selectplaylist')

def get_token():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        raise Exception('No token found')
    now = int(time.time())
    if token_info['expires_at'] - now < 60:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

@app.route('/selectplaylist')
def selectPlaylist():
    try:
        token_info= get_token()
    except Exception as e:
        print('try logging in again',e)
        return redirect('/')
    sp= spotipy.Spotify(auth=token_info['access_token'])
    user= sp.current_user()['id']
    app.logger.info(user)
    allPlaylists= sp.user_playlists(user=user,limit=50)['items']
    playName= [[i.get('name'),i.get('id')] for i in allPlaylists]
    playId= [i.get('id') for i in allPlaylists]
    return render_template('selectPlaylist.html',playName=playName,playId=playId)



@app.route('/playlist/<string:playlist_id>')
def playlist(playlist_id):
    try:
        token_info= get_token()
    except Exception as e:
        print('try logging in again',e)
        return redirect('/')
    sp= spotipy.Spotify(auth=token_info['access_token'])
    user= sp.current_user()['id']
    totalTracks= sp.playlist_items(playlist_id).get('total')
    if totalTracks>98:
        totalTracks= 98
    playTracks= sp.user_playlist_tracks(user=user, playlist_id= playlist_id)['items']
    trackID= [i.get('track').get('id') for i in playTracks]
    randSelector= [trackID[i] for i in range(randint(0,totalTracks-1))]
    features= sp.audio_features(tracks=randSelector)
    energies= sum([i.get('energy') for i in features])/len(randSelector)
    beats= round(sum([i.get('tempo') for i in features])/len(randSelector))
    live= sum([i.get('danceability') for i in features])/len(randSelector)
    key= sum([i.get('key') for i in features])/len(randSelector)
    playMode= [i.get('mode') for i in features]
    if mode(playMode) == 0:
        rota= -live
    else:
        rota= live
    palette = Cubehelix.make(start=energies, rotation= rota, n=len(randSelector))
    particleArray = palette.colors
    with open("static/colors.json", 'w') as f:
        json.dump(particleArray, f)
    with open("static/colors.json") as f:
        data = json.load(f)
    return render_template('processor.html', dim= beats, ang= totalTracks, live=live, key=key)







