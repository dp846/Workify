from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db=SQLAlchemy()

class Users(UserMixin,db.Model):
    __tablename__="users"
    id = db.Column(db.String(50), primary_key=True,autoincrement=False)
    access_token = db.Column(db.String(100))
    refresh_token = db.Column(db.String(100))
    expiry_date = db.Column(db.DateTime)
    points = db.Column(db.Integer)

    def __init__(self, id, access_token, refresh_token, expiry_date): 
        self.id = id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expiry_date = expiry_date
        self.points = 0

class Goals(db.Model): #productivity goals
    __tablename__="goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    goal_time = db.Column(db.Integer)
    date_created =  db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def __init__(self, user_id, goal_time, date_created, end_date):
        self.user_id = user_id
        self.goal_time = goal_time
        self.date_created = date_created
        self.end_date = end_date
        
class MusicGoals(db.Model):
    __tablename__="musicgoals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    music_feature = db.Column(db.String(50))
    feature_percentage = db.Column(db.Integer)
    date_created =  db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    def __init__(self, user_id, music_feature, feature_percentage, date_created, end_date):
        self.user_id = user_id
        self.music_feature = music_feature
        self.feature_percentage = feature_percentage
        self.date_created = date_created
        self.end_date = end_date

class WorkSessions(db.Model):
    __tablename__="worksessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    start_time=db.Column(db.DateTime)
    duration=db.Column(db.Float)
    productivity_score=db.Column(db.Float)
    listened_to_music=db.Column(db.Boolean)

    def __init__(self, user_id, start_time, duration,productivity_score,listened_to_music):  
        self.user_id = user_id
        self.start_time = start_time
        self.duration = duration
        self.productivity_score = productivity_score
        self.listened_to_music = listened_to_music

class TrackHistory(db.Model):
    __tablename__="trackhistory"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    track_id = db.Column(db.String(50), db.ForeignKey('tracks.id'))
    start_time=db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id','track_id', 'start_time', name='_track_start_time_uc',sqlite_on_conflict='IGNORE'),)

    def __init__(self,user_id, track_id, start_time):  
        self.track_id=track_id
        self.user_id=user_id
        self.start_time=start_time

class Tracks(db.Model):
    __tablename__="tracks"
    id = db.Column(db.String(25), primary_key=True)
    name = db.Column(db.String(50))
    duration=db.Column(db.Integer)
    danceability=db.Column(db.Float)
    energy=db.Column(db.Float)
    speechiness=db.Column(db.Float)
    acousticness=db.Column(db.Float)
    instrumentalness=db.Column(db.Float)
    liveness=db.Column(db.Float)
    valence=db.Column(db.Float)

    def __init__(self,id,name, duration, danceability,energy,speechiness,acousticness,instrumentalness,liveness,valence):     
        self.id=id
        self.name=name
        self.duration=duration
        self.danceability=danceability
        self.energy=energy
        self.speechiness=speechiness
        self.acousticness=acousticness
        self.instrumentalness=instrumentalness
        self.liveness=liveness
        self.valence=valence