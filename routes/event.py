
# create event page
from datetime import datetime
import json

from bson import ObjectId
from app import app, mongo,login_required
from flask import render_template, request, redirect, url_for, session



@app.route('/events/<eventId>')
def event_details(eventId):
    event = mongo.db.events.find_one({'_id': ObjectId(eventId)})
    # update view count
    mongo.db.events.update_one({'_id': ObjectId(eventId)}, {'$inc': {'viewCount': 1}})
    user = None
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})

    # get the events posts using artworkPosts field
    posts = [mongo.db.event_posts.find_one({'_id': ObjectId(postId)}) for postId in event['artworkPosts']]

    # get the artwork object for each post
    post_list = []
    for post in posts:
        artwork = mongo.db.artworks.find_one({'_id': post['artworkId']})
        user = mongo.db.profile_info.find_one({"username": post["owner"]})

        post_list.append({
            'post': post,
            'artwork': artwork,
            'user': user
        })

    return render_template('event_details.html', event=event, mongo=mongo, user=user, posts=post_list)


@app.route('/events')
def events():
    events = mongo.db.events.find({})
    return render_template('events.html', events=events, mongo=mongo)

@app.route('/events/join/<eventId>')
@login_required
def join_event(eventId):
    username = session['username']
    # push event to user's joinedEvents array
    mongo.db.users.update_one({'username': username}, {'$push': {'joinedEvents': ObjectId(eventId)}})
    return redirect(url_for('event_details', eventId=eventId))

@app.route('/events/leave/<eventId>')
@login_required
def leave_event(eventId):
    event = mongo.db.events.find_one({'_id': ObjectId(eventId)})
    username = session['username']
    # remove event from user's joinedEvents array
    mongo.db.users.update_one({'username': username}, {'$pull': {'joinedEvents': ObjectId(eventId)}})
    return redirect(url_for('event_details', eventId=eventId))

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        eventName = request.form['eventName']
        eventLabelsData = request.form['eventLabelsData']
        eventLabels = json.loads(eventLabelsData)
        eventDescription = request.form['eventDescription']
        createdBy = session['username']
        now = datetime.now()
        createdAt = now.strftime("%d/%m/%Y %H:%M:%S")

        mongo.db.events.insert_one({
            'eventName': eventName,
            'eventLabels': eventLabels,
            'eventDescription': eventDescription,
            'createdBy': createdBy,
            'createdAt': createdAt,
            'postedArtworkCount': 0,
            'viewCount': 0,
            'artworkPosts': [],
            'lastPostedBy': '',
            'lastPostedAt': ''
        })
        return redirect(url_for('events'))

    return render_template('create_event.html')
    

@app.route('/event/p/<post_id>')
def event_post_page(post_id):
    post = mongo.db.event_posts.find_one({"_id": ObjectId(post_id)})
    artwork = mongo.db.artworks.find_one({"_id": post["artworkId"]})
    user = mongo.db.profile_info.find_one({"username": post["owner"]})
    # update view count
    print(artwork)
    mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'viewCount': 1}})
    return render_template('event_post.html', post=post, artwork=artwork, user=user, mongo=mongo)