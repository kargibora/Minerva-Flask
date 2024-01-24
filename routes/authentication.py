from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, S3_BUCKET, s3_client
from flask import request, render_template, redirect, url_for, session, flash
from utils.identicon import generate
from utils.bucket_utils import upload_to_s3
import io
import random 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = mongo.db.account_info.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")

    # get 5 last artwork from the database
    artworks = list(mongo.db.artworks.aggregate([{ '$sample': { 'size': 10} }]))
    return render_template("login.html",artworks_front = artworks[:9], artworks_back = artworks[9:])

@app.route("/logout")
def logout():
    session.pop("username", None)

    return redirect(url_for("login"))
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register'))

        existing_user = mongo.db.account_info.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        identicon_image = generate(username)

        # convert Image object to bytes
        byte_arr = io.BytesIO()
        identicon_image.save(byte_arr, format='JPEG')
        byte_arr = byte_arr.getvalue()

        if identicon_image is not None:
            identicon_filename = f'{username}.jpeg'
            # upload identicon to S3
            identicon_url = upload_to_s3(S3_BUCKET, s3_client, file_type='image/jpeg', file_name=identicon_filename, file_byte=byte_arr)


        mongo.db.account_info.insert_one({'username': username, 'email': email, 'password': hashed_password})
        mongo.db.profile_info.insert_one({
            'username': username,
            'name': '',
            'surname': '',
            'dateOfBirth': '',
            'location': '',
            'bio': '',
            'profilePictureS3URL': 'https://upload.wikimedia.org/wikipedia/commons/a/ac/Default_pfp.jpg' if identicon_url is None else identicon_url, 
            'gender': ''
        })

        mongo.db.users.insert_one({
            'username': username,
            'following': [],
            'followers': [],
            'posts': [],
            'artworks': [],
            'likedPosts': [],
            'joinedEvents': [],
            'isVerified': False,
            'viewCount': 0,
        })
        
        session['username'] = username
        profile = mongo.db.profile_info.find_one({"username": username})
        return render_template('settings.html', profile=profile)

    return render_template('register.html')