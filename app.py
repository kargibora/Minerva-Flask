from datetime import datetime
import random
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, render_template_string, send_file
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId, json_util
from functools import wraps
from werkzeug.utils import secure_filename
import os


from utils.bucket_utils import upload_to_s3, check_bucket_exists,create_s3_client

# --- SETUP --- 

app = Flask(__name__)


# allow  https://kbora-minerva-workspace.hf.space/ to access the backend
CORS(app, resources={r"/*": {"origins": "https://kbora-minerva-workspace.hf.space/"}})

#app.config["MONGO_URI"] = "mongodb+srv://e2381036:w2ezVTDtU3jxXYh7@yigitify.g7walwv.mongodb.net/minerva"
app.config["MONGO_URI"] = "<MONGO_URI_HERE>"
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# CORS is needed for the frontend to be able to access the backend
mongo = PyMongo(app)

with open("credentials.txt", "r") as f:
    AWS_ACCESS_KEY = f.readline().strip()
    AWS_SECRET_KEY = f.readline().strip()
    AWS_REGION = f.readline().strip()

# Replace these values with your AWS credentials and the desired S3 bucket name
S3_BUCKET = "minerva-phase-1"
s3_client = create_s3_client(AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION)
check_bucket_exists(S3_BUCKET, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION)

# --- ROUTES ---

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

app.secret_key = "your_secret_key"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            flash("Please login to view this page.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

import routes.api
import routes.main
import routes.authentication
import routes.generate
import routes.profile
import routes.post
import routes.artworks
import routes.event

def create_random_artwork_and_post():
    images = [
        'https://miro.medium.com/v2/resize:fit:4800/format:webp/1*qRj66PNZpD_zAbtyIWOPkQ.png',
        'https://miro.medium.com/v2/resize:fit:4800/format:webp/1*UuPtCvOQK-uU3ThhFPn_tg.png',
        'https://miro.medium.com/v2/resize:fit:4800/format:webp/1*9st_oq2ctceLfe3jPV9qiA.jpeg'
    ]

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    artwork = mongo.db.artworks.insert_one({
        'owner': 'admin',
        'generativeCaption': 'This is a generative caption',
        'imageURLS3': random.choice(images),
        'dateGenerated': dt_string
    })

    # create a post with the artwork id
    """
    - owner: username
    - caption
    - artworkId (which is MongoDB Object id for artwork)
    - likes: []username
    - comments: Map{username: ‘comment’}
    - likeCount
    - commentCount
    - datePosted
    """
    post = mongo.db.posts.insert_one({
        'owner': 'admin',
        'caption': 'This is a post caption',
        'artworkId': artwork.inserted_id,
        'likes': [],
        'comments': {},
        'likeCount': 0,
        'commentCount': 0,
        'datePosted': dt_string
    })

    # push the artwork id and post id to the user's artworks array
    mongo.db.users.update_one(
        {"username": 'admin'},
        {
            "$push": {
                "artworks": artwork.inserted_id,
                "posts": post.inserted_id
            }
        }
    )

# health check
@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8080)
    app.run(debug=True)
