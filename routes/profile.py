from app import app, mongo,login_required
from flask import render_template, request, redirect, url_for, session
from bson import ObjectId, json_util
from utils.date import parse_date

@app.route('/profile/<username>')
def profile(username):
    page = request.args.get('page', default=1, type=int)

    # make sure that page > 0
    if page < 1:
        page = 1

    per_page = 9  # posts per page
    start = (page - 1) * per_page
    end = start + per_page

    user = mongo.db.users.find_one({"username": username})
    profile = mongo.db.profile_info.find_one({"username": username})

    # sort by the date which is in the format of day/month/year hour/second
    posts = list(mongo.db.posts.find({"owner": username}))
    posts.sort(key=parse_date, reverse=True)
    
    total_pages = -(-len(posts) // per_page)  # Ceiling division
    # increase view count
    if username in session and session.get('username') != username:
        mongo.db.users.update_one({"username": username}, {'$inc': {'viewCount': 1}})

    return render_template('profile.html', profile=profile, user=user, mongo=mongo, posts=posts[start:end], page=page, total_pages=total_pages)

# TODO : All posts should have a way to show who liked them
@app.route('/profile/<username>/liked-posts')
def liked_posts(username):
    page = request.args.get('page', default=1, type=int)

    # make sure that page > 0
    if page < 1:
        page = 1

    per_page = 9  # posts per page
    start = (page - 1) * per_page
    end = start + per_page

    user = mongo.db.users.find_one({"username": username})
    profile = mongo.db.profile_info.find_one({"username": username})

    # fetch liked posts from the database in user.likedPosts array
    liked_posts_ids = user.get('likedPosts', [])

    # convert post ids to ObjectId
    liked_posts = [mongo.db.posts.find_one({'_id': ObjectId(post_id)}) for post_id in liked_posts_ids][::-1] # liked in reverse order

    # calculate total_pages
    total_pages = len(liked_posts_ids) // per_page
    if len(liked_posts_ids) % per_page > 0:
        total_pages += 1

    return render_template('profile.html', profile=profile, user=user, mongo=mongo, posts=liked_posts[start:end], page=page, total_pages=total_pages)

@app.route('/accounts/edit', methods=['GET', 'POST'])
@login_required
def settings():
    username = session['username']
    alerts = []
    if request.method == 'POST':
        # Get the form data and update the database
        name = request.form['name']
        surname = request.form['surname']
        dateOfBirth = request.form['dateOfBirth']
        location = request.form['location']
        bio = request.form['bio']
        gender = request.form['gender']

        mongo.db.profile_info.update_one(
            {"username": username},
            {
                "$set": {
                    "name": name,
                    "surname": surname,
                    "dateOfBirth": dateOfBirth,
                    "location": location,
                    "bio": bio,
                    "gender": gender,
                }
            }
        )
        alerts.append({'alert_id': '3', 'message': 'Profile updated successfully!'})

    profile = mongo.db.profile_info.find_one({"username": username})
    return render_template('settings.html', profile=profile, alerts=alerts)