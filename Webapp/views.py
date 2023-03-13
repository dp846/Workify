from flask import render_template, redirect, request,session, url_for
from flask_classful import FlaskView, route
from flask_login import login_user, current_user, logout_user,login_required
from db_schema import db, Users, Goals, MusicGoals, WorkSessions, Tracks, TrackHistory

from utils.music_utils import *
from utils.database_utils import *
from utils.url_utils import *

from datetime import datetime,timedelta

from random import randint
import json

database=DatabaseAccess(db, Users, Goals, MusicGoals, WorkSessions, TrackHistory, Tracks)
app_paths=Paths()  

class LandingView(FlaskView):
    """ 
    Returns the html template for the landing page. 
    Redirects to the Spotify login page or the dashboard if the user is already logged in.
    Upon spotify authentication, the user is redirected to the dashboard.
    Route "/"
    """

    def index(self):
        return render_template("landing_page.html")

    @route('/authenticate/')
    def authenticate(self):
        "If the user is already logged in, redirects to the dashboard. Otherwise, redirects to the Spotify login page."

        if not current_user.is_authenticated:
            return redirect(SpotifyClient.request_user_auth())
        else:
            user = database.get_user(current_user.id)
            self.update_session(user)
            return redirect("/home") 

    @route('/callback/')
    def callback(self):
        "If the user did not authorize the app, no change. Otherwise, redirects to the dashboard."

        if request.args.get("error")=="access_denied":
            return ("",204)
        else:
            new_user_details=SpotifyClient.get_user_details(request.args.get("code"))
            user=database.add_user(*new_user_details)

            self.update_session(user)
            login_user(user)
            return redirect("/home")

    def update_session(self, user):
        user_details = user.__dict__.copy()
        del user_details["_sa_instance_state"]
        session.update(user_details)

    @route('/logout/')
    @login_required
    def logout(self):
        logout_user()
        return redirect("/")

class HomeView(FlaskView):
    """
    Returns the html template for the home page.
    Route "/home"
    """

    @login_required
    def index(self):
        return render_template("home.html")

class GoalView(FlaskView):
    """
    Returns the html template for the goals page.
    Depending on the url path, the user is directed to the appropriate goal page.
    Contains methods for adding a new goal, deleting a goal, and updating a goal.
    Route "/goals"
    """

    @login_required
    def index(self):
        return redirect(url_for("GoalView:productivity_goal"))
    
    def productivity_goal(self):
        """
        Retrieves the productivity goals for the user and returns the html template for the productivity goal page.
        Route "/goals/productivity"
        """

        goals=database.get_productivity_goals(current_user.id)
        context={"type":"productivity","goals":goals}
        
        for goal in goals:
            goal_time=goal.goal_time
            if goal_time == 0:
                goal.progress = 100
            else:
                goal.progress=int(database.get_total_session_time_between_time(current_user.id,goal.date_created,goal.end_date) / goal_time * 100)
            goal.progress=goal.progress if goal.progress<=100 else 100

        return render_template("goal.html",context=context, points=database.get_user_points(current_user.id))

    def music_goal(self):
        """
        Retrieves the music goals for the user and returns the html template for the music goal page.
        Route "/goals/music"
        """

        goals=database.get_music_goals(current_user.id)
        feature_names = {"acousticness":"Acoustic","danceability":"Danceability","energy":"Energy","instrumentalness":"Instrumental","liveness":"Liveness","speechiness":"Speech","valence":"Valence"}
        context={"type":"music","goals":goals,"feature_names":feature_names}

        for goal in goals:
            average_audio_features = database.get_average_track_properties_between_time(current_user.id,goal.date_created,goal.end_date)
            goal.progress = int(average_audio_features[goal.music_feature]*10000/goal.feature_percentage)
            goal.progress=goal.progress if goal.progress<=100 else 100

        return render_template("goal.html",context=context, points=database.get_user_points(current_user.id))

    def post(self):
        "Adds a new goal to the database."

        form_data=request.form
        if form_data["type"] == "productivity":
            goal_time=form_data["goal_time"]
            if form_data["start_date"]=="" or form_data["end_date"]=="" or form_data["end_date"] < form_data["start_date"] or not goal_time.isnumeric() or int(goal_time) <= 0:
                return ("",204)
            start_date=datetime.strptime(form_data["start_date"],"%Y-%m-%d")
            end_date=datetime.strptime(form_data["end_date"],"%Y-%m-%d")
            database.add_productivity_goal(current_user.id,int(goal_time),start_date,end_date)
        elif form_data["type"] == "music":
            if form_data["start_date"]=="" or form_data["end_date"]=="" or form_data["music_feature"] =="" or not form_data["feature_percentage"].isnumeric() or int(form_data["feature_percentage"]) <= 0 or int(form_data["feature_percentage"])> 100:
                return ("",204)
            feature = form_data["music_feature"]
            percentage = form_data["feature_percentage"]
            start_date=datetime.strptime(form_data["start_date"],"%Y-%m-%d")
            end_date=datetime.strptime(form_data["end_date"],"%Y-%m-%d")
            database.add_music_goal(current_user.id, feature, percentage, start_date, end_date)
            return redirect(url_for("GoalView:music_goal"))

        return redirect(url_for(f"GoalView:{form_data['type']}_goal"))

    @route('delete_goal', methods=['POST'])
    def delete_goal(self):
        "Deletes a goal from the database, if the user is the owner of the goal."

        form_data=request.form
        goal_id=int(form_data["goal_id"])
        if form_data["goal_type"] == "productivity":
            database.delete_productivity_goal(goal_id)
        else:
            database.delete_music_goal(goal_id)

        return redirect(url_for(f"GoalView:{form_data['goal_type']}_goal"))

    @route('update_goal', methods=['POST'])
    def update_goal(self):
        "Updates a goal from the database, if the user is the owner of the goal."

        form_data=request.form
        goal_id=int(form_data["goal_id"])
        new_value = form_data["goal_value"].replace("%","")
        start_date=datetime.strptime(form_data["start_date"],"%Y-%m-%d")
        end_date=datetime.strptime(form_data["end_date"],"%Y-%m-%d")

        if start_date=="" or end_date=="" or end_date < start_date or not new_value.isnumeric():
            return ("",204)

        if form_data["goal_type"] == "productivity":
            if int(new_value) <= 0:
                return ("",204)
            database.update_productivity_goal(goal_id,new_value,start_date,end_date)
        else:
            if not int(new_value) in range(1,101):
                return ("",204)
            database.update_music_goal(goal_id,new_value,start_date,end_date)

        return redirect(url_for(f"GoalView:{form_data['goal_type']}_goal"))


class TaskView(FlaskView):
    """
    Returns the html template for the timer page.
    After session completion, the session data is added to the database.
    The users recently played music is retrieved and added to the database.
    Route "/timer"
    """

    @login_required
    def index(self):
        return render_template("timer.html", points=database.get_user_points(current_user.id))

    def post(self):
        "Adds a new work session to the database and retrieves users recently played music."

        form_data=request.form
        hours,minutes,seconds=form_data["time"].split(":")
        time_elapsed=timedelta(hours=int(hours),minutes=int(minutes),seconds=int(seconds))
        database.add_session(current_user.id,datetime.now()-time_elapsed,round(time_elapsed / timedelta(hours=1),4),form_data["rating"],True)

        if (datetime.now(session["expiry_date"].tzinfo) >= session["expiry_date"]):
            new_access_token = SpotifyClient.get_refreshed_access_token(session["refresh_token"])
            database.update_access_token(current_user.id,*new_access_token)
            session["access_token"]=new_access_token[0]
            session["expiry_date"]=new_access_token[1]
            
        recently_played = SpotifyClient.get_recently_played_tracks(session["access_token"])
        database.add_to_tracks_history(current_user.id,recently_played)
        
        diff_in_seconds = time_elapsed.total_seconds()
        rating = int(form_data["rating"])

        if rating >= 8:  # If prod rating is 8 or higher, 1.5x time spent
            multiplier = 1.5
        elif rating == 7:  # If prod rating is 7, 1.25x time spent
            multiplier = 1.25
        elif rating <= 6 and rating >= 4:
            multiplier = 1
        elif rating == 3:  # If prod rating is 3, 0.75x time spent
            multiplier = 0.75
        elif rating <= 2:  # If prod rating is 2 or lower, 0.5x time spent
            multiplier = 0.5
        database.update_user_points(current_user.id,database.get_user_points(current_user.id) + round(multiplier*diff_in_seconds))

        return redirect("/timer")


class ProgressView(FlaskView):
    """
    Returns the html template for the progress page.
    Route "/progress"
    """

    @login_required
    def index(self):
        num_days = 14 #Number of days to look back on in the graph
        
        date_today = datetime.today()
        start_date = date_today - timedelta(days=num_days)
        date_list = [date_today - timedelta(days=x) for x in range(num_days)] #Past 2 weeks

        xValues = ["" for x in range (num_days)]
        yValues = [0 for x in range(num_days)]
        most_productive_day = date_today
        highest_avg_rating = 0

        for i, current_date in enumerate(date_list):
            date_before = current_date - timedelta(days=1)
            time_worked = database.get_total_session_time_between_time(current_user.id,date_before, current_date) #In hours

            yValues[i] = time_worked #Conversion from hours to minutes
            xValues[i] = current_date.strftime("%Y-%m-%d") #String of the date will act as the x axis labels

            day_avg_rating = database.get_average_self_rating_between_time(current_user.id, date_before, current_date) * time_worked
            if day_avg_rating > highest_avg_rating:
                most_productive_day = date_before
                highest_avg_rating = day_avg_rating


        most_productive_properties = database.get_average_track_properties_between_time(current_user.id, most_productive_day, most_productive_day+timedelta(days=1))
        labels = []
        data = []
        data2 = []

        xValues.reverse()
        yValues.reverse()

        avg_track_properties = database.get_average_track_properties_between_time(current_user.id,start_date,date_today)
        for prop, value in avg_track_properties.items():
            labels.append(prop.upper())
            data.append(value)

        if avg_track_properties.items() != most_productive_properties:
            for prop, value in most_productive_properties.items():
                data2.append(value)


        context = {"xValues" : json.dumps(xValues), "yValues" : json.dumps(yValues),"data" : json.dumps(data), "labels" : json.dumps(labels), "data2" : json.dumps(data2)}
        return render_template("progress.html", **context, points=database.get_user_points(current_user.id))


app_paths.add_path(LandingView,route_base='/')
app_paths.add_path(HomeView,route_base='/home')
app_paths.add_path(GoalView,route_base='/goals')
app_paths.add_path(TaskView,route_base='/timer')
app_paths.add_path(ProgressView,route_base='/progress')