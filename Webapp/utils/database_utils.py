from sqlalchemy import exc

class DatabaseAccess:
    def __init__(self,db,Users,Goals,MusicGoals,WorkSessions,TrackHistory,Tracks) -> None:
        self.db=db
        self.Users=Users
        self.ProductivityGoals = Goals
        self.MusicGoals = MusicGoals
        self.WorkSessions = WorkSessions
        self.TrackHistory = TrackHistory
        self.Tracks = Tracks
        self.audio_features = ['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence']

    # User related CRUD operations
    def get_user_points(self,user_id):
        user = self.Users.query.filter_by(id=user_id).first()
        return user.points

    def add_user(self,id,access_token,request_token,expiry_date):
        user=self.Users(id,access_token,request_token,expiry_date)
        try:
            self.db.session.add(user)
            self.db.session.commit()
        except exc.IntegrityError:
            self.db.session.rollback()
            self.get_user(id)
        return user

    def get_user(self,id):
        user = self.Users.query.filter_by(id=id).first()
        return user

    def delete_user(self,id):
        self.Users.query.filter_by(id=id).delete()
        self.db.session.commit()

    def update_access_token(self,user_id,new_access_token,expiry_date):
        self.Users.query.filter_by(id=user_id).update({"access_token": new_access_token, "expiry_date": expiry_date})
        self.db.session.commit()

    def update_user_points(self,user_id,points_change):
        user = self.Users.query.filter_by(id=user_id).first()
        user.points = points_change
        self.db.session.commit()
    
    # Goals related CRUD operations
    def add_productivity_goal(self,id,goal_time,date_created,end_date):
        goal=self.ProductivityGoals(id,goal_time,date_created,end_date)
        self.db.session.add(goal)
        self.db.session.commit()
        return goal 
    
    def add_music_goal(self,id,music_feature, feature_percentage,date_created,end_date):
        goal=self.MusicGoals(id,music_feature,feature_percentage,date_created,end_date)
        self.db.session.add(goal)
        self.db.session.commit()
        return goal   

    def get_productivity_goals(self,id):
        goals=self.ProductivityGoals.query.filter_by(user_id=id).all()
        return goals
    
    def get_music_goals(self,id):
        goals=self.MusicGoals.query.filter_by(user_id=id).all()
        return goals

    def get_productivity_goal_user_id(self,goal_id):
        goals=self.ProductivityGoals.query.filter_by(id=goal_id).first()
        return goals.user_id
    
    def get_music_goal_user_id(self,goal_id):
        goals=self.MusicGoals.query.filter_by(id=goal_id).first()
        return goals.user_id
        
    def delete_productivity_goal(self,id):
        self.ProductivityGoals.query.filter_by(id=id).delete()
        self.db.session.commit()
        
    def delete_music_goal(self,id):
        self.MusicGoals.query.filter_by(id=id).delete()
        self.db.session.commit()

    def update_productivity_goal(self,goal_id,goal_time,start_date,end_date):
        self.ProductivityGoals.query.filter_by(id=goal_id).update({"goal_time": goal_time, "date_created": start_date, "end_date": end_date})
        self.db.session.commit()

    def update_music_goal(self,goal_id,feature_percentage,start_date,end_date):
        self.MusicGoals.query.filter_by(id=goal_id).update({"feature_percentage": feature_percentage, "date_created": start_date, "end_date": end_date})
        self.db.session.commit()

    # Work sessions related CRUD operations
    def add_session(self,user_id,start_time,duration,productivity_score,listened_to_music):
        work_sessions = self.WorkSessions(user_id,start_time,duration,productivity_score,listened_to_music)
        self.db.session.add(work_sessions)
        self.db.session.commit()
        return work_sessions

    def get_user_sessions(self,user_id):
        work_sessions = self.WorkSessions.query.filter_by(user_id=user_id).all()
        return work_sessions

    def get_total_session_time_between_time(self,user_id,start_time,end_time):
        work_sessions = self.WorkSessions.query.filter_by(user_id=user_id).filter(self.WorkSessions.start_time.between(start_time,end_time)).all()
        total_time = sum([session.duration for session in work_sessions])
        return total_time

    def get_average_self_rating_between_time(self,user_id,start_time,end_time):
        work_sessions = self.WorkSessions.query.filter_by(user_id = user_id).filter(self.WorkSessions.start_time.between(start_time, end_time)).all()

        if len(work_sessions) == 0:
            return 0
        total = sum([s.productivity_score for s in work_sessions])

        return total/len(work_sessions)

    # Track related CRUD operations
    def add_track(self,track_id,name,duration,commit=True,**kwargs):
        track = self.Tracks(track_id,name,duration,**kwargs)
        self.db.session.add(track)
        if commit:
            self.db.session.commit()
        return track

    def track_exists(self,track_id):
        track_exists = self.Tracks.query.filter_by(id=track_id).first() is not None
        return track_exists

    # Track history related CRUD operations
    def get_average_track_properties_between_time(self,user_id,start_time,end_time):
        tracks = self.TrackHistory.query.filter_by(user_id=user_id).filter(self.TrackHistory.start_time.between(start_time,end_time)).all()
        average_track_properties = dict.fromkeys(self.audio_features,0)

        if len(tracks) == 0:
            return average_track_properties

        for track in tracks:
            track_properties = self.Tracks.query.filter_by(id=track.track_id).first()
            for key,value in track_properties.__dict__.items():
                if key in self.audio_features:
                    average_track_properties[key] += value

        for key,value in average_track_properties.items():
            average_track_properties[key] = round(value/len(tracks),4)
        return average_track_properties
        
    def add_to_tracks_history(self,user_id,tracks):
        tracks.reverse()
        for track in tracks:
            if not self.track_exists(track.id):
                self.add_track(track.id,track.name,track.duration,commit=False,**(track.features))

            track_object = self.TrackHistory(user_id,track.id,track.played_at)
            self.db.session.add(track_object)

        self.db.session.commit()
        return track_object