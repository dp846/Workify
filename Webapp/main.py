from flask import Flask
from flask_login import LoginManager
from db_schema import db, Users
from views import app_paths
import os

# Create flask application and set configuration variables
app = Flask(__name__)
app_paths.register(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workify.sqlite"#+os.getenv("DB_NAME")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"]="asdasdsad"#os.getenv("SECRET_KEY")
app.config["FLASK_RUN_PORT"]="8000"#os.getenv("FLASK_RUN_PORT")

# Create login manager object to authenticate users
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "LandingView:index"

@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)
    
# Create database if it does not exist
db.init_app(app)
if not os.path.isfile("workify.sqlite"):
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    app.run(port="8000")
