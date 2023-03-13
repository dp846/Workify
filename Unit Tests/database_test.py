from datetime import datetime, timedelta
import unittest
import sys
import os
import flask_sqlalchemy
from Webapp.utils import database_utils
from Webapp.utils.music_utils import Track

sys.path.append(os.path.join(os.path.dirname(__file__),"..", 'Webapp'))
track_features=['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence']

class TestDatabase(unittest.TestCase):
	def setUp(self):
		from Webapp.main import app
		from Webapp.views import db,Users, Goals, MusicGoals, WorkSessions, TrackHistory, Tracks
		app.app_context().push()
		self.database = database_utils.DatabaseAccess(db,Users, Goals, MusicGoals, WorkSessions, TrackHistory, Tracks)

class TestInit(TestDatabase):
	def test_initial_user_relation(self):
		self.assertEqual(isinstance(self.database.Users,flask_sqlalchemy.model.DefaultMeta),True)

	def test_initial_worksession_relation(self):
		self.assertEqual(isinstance(self.database.WorkSessions,flask_sqlalchemy.model.DefaultMeta),True)

	def test_initial_productivity_goal_relation(self):
		self.assertEqual(isinstance(self.database.ProductivityGoals,flask_sqlalchemy.model.DefaultMeta),True)

	def test_initial_music_goals_relation(self):
		self.assertEqual(isinstance(self.database.MusicGoals,flask_sqlalchemy.model.DefaultMeta),True)

	def test_initial_trackhistory_relation(self):
		self.assertEqual(isinstance(self.database.TrackHistory,flask_sqlalchemy.model.DefaultMeta),True)

	def test_initial_tracks_relation(self):
		self.assertEqual(isinstance(self.database.Tracks,flask_sqlalchemy.model.DefaultMeta),True)

class TestInsert(TestDatabase):
	def test_insert_user_tuple(self):
		result=self.database.add_user("user123","B345UIHG23VHUJ234","32B234PIOH213JB123",datetime.now())
		self.assertEqual(isinstance(result,self.database.Users),True)

	def test_insert_worksession_tuple(self):
		result=self.database.add_session("user123",datetime.now(),12,9,True)
		self.assertEqual(isinstance(result,self.database.WorkSessions),True)
	
	def test_insert_productivity_goal_tuple(self):
		result=self.database.add_productivity_goal("user123",2,datetime.now(),datetime.now()+timedelta(days=1))
		self.assertEqual(isinstance(result,self.database.ProductivityGoals),True)

	def test_insert_music_goal_tuple(self):
		result=self.database.add_music_goal("user123","valence",80,datetime.now(),datetime.now()+timedelta(days=1))
		self.assertEqual(isinstance(result,self.database.MusicGoals),True)

	def test_insert_track_tuple(self):
		result=self.database.add_track(1,"Never Gonna Give You Up",300,True,**dict.fromkeys(track_features, 0.1))
		self.assertEqual(isinstance(result,self.database.Tracks),True)

	def test_insert_trackhistory_tuple(self):
		track = Track(2,"Never Gonna Give You Up",300,"2000-01-01T00:00:00",dict.fromkeys(track_features, 0.1))
		result=self.database.add_to_tracks_history(1,[track])
		self.assertEqual(isinstance(result,self.database.TrackHistory),True)

class TestQueries(TestDatabase):
	
	def test_get_user(self):
		result=self.database.get_user("user123")
		self.assertEqual(result.id,"user123")
	
	def test_get_user_points(self):
		result=self.database.get_user_points("user123")
		self.assertEqual(result,0)

	def test_get_productivity_goals(self):
		result=self.database.get_productivity_goals("user123")
		self.assertEqual(len(result),1)
		self.assertIsInstance(result[0],self.database.ProductivityGoals)

	def test_get_music_goals(self):
		result=self.database.get_music_goals("user123")
		self.assertEqual(len(result),1)
		self.assertIsInstance(result[0],self.database.MusicGoals)

	def test_get_productivity_goal_user_id(self):
		result=self.database.get_productivity_goal_user_id(1)
		self.assertEqual(result,"user123")

	def test_get_music_goal_user_id(self):
		result=self.database.get_music_goal_user_id(1)
		self.assertEqual(result,"user123")

	def test_get_user_sessions(self):
		result=self.database.get_user_sessions("user123")
		self.assertEqual(len(result),1)

	def test_get_total_session_time_between_time(self):
		result=self.database.get_total_session_time_between_time("user123",datetime.now()-timedelta(days=1),datetime.now())
		self.assertEqual(result,12)

	def test_get_average_self_rating_between_time(self):
		result=self.database.get_average_self_rating_between_time("user123",datetime.now()-timedelta(days=1),datetime.now())
		self.assertEqual(result,9)

	def test_track_exists(self):
		result=self.database.track_exists(1)
		self.assertEqual(result,True)

	def test_get_average_track_properties_between_time(self):
		result=self.database.get_average_track_properties_between_time("user123",datetime(1999,12,31),datetime.now())
		self.assertEqual(result,dict.fromkeys(track_features, 0))	

class TestDelete(TestDatabase):
	def test_delete_user_record(self):
		self.database.delete_user("user123")
		result=self.database.Users.query.filter_by(id="user123").first()
		self.assertEqual(result,None)

	def test_delete_productivity_goal_record(self):
		self.database.delete_productivity_goal(1)
		result=self.database.ProductivityGoals.query.filter_by(id=1).first()
		self.assertEqual(result,None)

	def test_delete_music_goal_record(self):
		self.database.delete_music_goal(1)
		result=self.database.MusicGoals.query.filter_by(id=1).first()
		self.assertEqual(result,None)


if __name__ == '__main__':
	unittest.main()