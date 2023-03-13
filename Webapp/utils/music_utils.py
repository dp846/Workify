import base64
from datetime import datetime,timedelta
from urllib.parse import urlencode
import requests
import os

class Track():
    def __init__(self, id, name, duration, played_at, features={}):
        self.id = id
        self.name = name
        self.played_at = datetime.strptime(played_at[:played_at.rindex(":")], '%Y-%m-%dT%H:%M')
        self.duration = int(duration/1000)
        self.features = features

    def __repr__(self):
         return (f"{self.name} played at {self.played_at} and has audio features: {self.features}\n")

class SpotifyRequestURLs:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI")

    ##These values are the ones to hard code in if the above environmental variables do not work
    # client_id="f9a49012a8304da3945bd360249c96bb"
    # client_secret="e03ac794f24e4884a0862a66e3157102"
    # redirect_uri="http://127.0.0.1:8000/callback/"

    fetch_limit = 50

    @staticmethod
    def get_client_data():
        return base64.b64encode((f"{SpotifyRequestURLs.client_id}:{SpotifyRequestURLs.client_secret}").encode()).decode()

    @staticmethod
    def request_user_auth_url():
        url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id" : SpotifyRequestURLs.client_id,
            "response_type" : "code",
            "redirect_uri" : SpotifyRequestURLs.redirect_uri,
            "scope" : "user-read-recently-played playlist-modify-public user-read-email"
        }
        return (url, params, "", "")

    @staticmethod
    def request_access_token_url(oauth_code):
        url = "https://accounts.spotify.com/api/token"
        body = {
            "grant_type" : "authorization_code",
            "code" : f"{oauth_code}",
            "redirect_uri" : SpotifyRequestURLs.redirect_uri,
        }
        headers = {
            "Content-Type" : "application/x-www-form-urlencoded",
            "Authorization" : f"Basic {SpotifyRequestURLs.get_client_data()}"
        }

        return (url, "", body, headers)

    @staticmethod
    def get_refreshed_token_url(refresh_token):
        url = "https://accounts.spotify.com/api/token"
        body = {    
            "grant_type" : "refresh_token",
            "refresh_token" : f"{refresh_token}"
        }
        headers = {
            "Content-Type" : "application/x-www-form-urlencoded",
            "Authorization" : f"Basic {SpotifyRequestURLs.get_client_data()}"
        }

        return (url, "", body, headers)

    @staticmethod
    def get_user_profile_url(oauth_token):
        url = "https://api.spotify.com/v1/me"
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {oauth_token}"
        }

        return (url, "", "", headers)

    @staticmethod
    def get_recently_played_url(access_token):
        url = "https://api.spotify.com/v1/me/player/recently-played"
        params = {
            "limit" : SpotifyRequestURLs.fetch_limit
        }
        headers={
            "Content-Type":"application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        return (url, params, "", headers)

    @staticmethod
    def get_track_features_url(access_token, tracks):
        url = "https://api.spotify.com/v1/audio-features/"
        params = {"ids" : ','.join(tracks)}
        headers = {
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {access_token}"
        }

        return (url, params, "", headers)

class SpotifyAPIRequest:
    @staticmethod
    def send_request(url,params,body,headers,method):
        if method=="POST":
            response=requests.post(url,params=params,data=body,headers=headers)
        else:
            response=requests.get(url,params=params,data=body,headers=headers)

        if response.status_code>200:
            raise Exception(f"Status code {response.json()}")
        return response.json()



class SpotifyClient:
    key_features=['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence']

    @staticmethod
    def encode_url(url,params):
        return url+"?"+urlencode(params)

    @staticmethod
    def get_refreshed_access_token(refresh_token):
        url,params,body,headers=SpotifyRequestURLs.get_refreshed_token_url(refresh_token)
        token_data = SpotifyAPIRequest.send_request(url,params,body,headers,"POST")
        expiry_date=datetime.now()+timedelta(seconds=int(token_data["expires_in"])-60)

        return (token_data["access_token"], expiry_date)

    @staticmethod
    def get_track_features(access_token,tracks):
        recently_played_ids=[track.id for track in tracks]
        url,params,body,headers=SpotifyRequestURLs.get_track_features_url(access_token,recently_played_ids)
        response=SpotifyAPIRequest.send_request(url,params,body,headers,"GET")
        return response['audio_features']

    @staticmethod
    def get_recently_played_tracks(access_token):
        url,params,body,headers=SpotifyRequestURLs.get_recently_played_url(access_token)
        response = SpotifyAPIRequest.send_request(url,params,body,headers,"GET")
        recently_played=[Track(track["track"]["id"],track["track"]["name"],track["track"]["duration_ms"],track["played_at"]) for track in response["items"]]
        features = SpotifyClient.get_track_features(access_token,recently_played)

        for track,track_feature in enumerate(features):
            for key_feature in SpotifyClient.key_features:
                recently_played[track].features[key_feature]=track_feature[key_feature]
        return recently_played

    @staticmethod
    def request_user_auth():
        url, params, body, headers = SpotifyRequestURLs.request_user_auth_url()
        return SpotifyClient.encode_url(url,params)

    @staticmethod
    def get_user_details(auth_token):
        url,params,body,headers=SpotifyRequestURLs.request_access_token_url(auth_token)
        token_data=SpotifyAPIRequest.send_request(url,params,body,headers,"POST")
        access_token=token_data["access_token"]
        refresh_token=token_data["refresh_token"]
        expires_in=int(token_data["expires_in"])

        url,params,body,headers=SpotifyRequestURLs.get_user_profile_url(access_token)
        user_data=SpotifyAPIRequest.send_request(url,params,body,headers,"GET")
        print(user_data)
        user_id=user_data['id']

        expiry_date=datetime.utcnow()+timedelta(seconds=expires_in-60)
        
        return (user_id,access_token,refresh_token,expiry_date)

