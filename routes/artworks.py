from app import app, mongo, login_required
from flask import render_template, request, redirect, url_for, session

@app.route('/manage_artworks')
@login_required
def manage_artworks():
    # get the user from the database
    user = mongo.db.users.find_one({"username": session.get('username')})

    # get the joinedEvents id fields
    joinedEventsIds = user.get('joinedEvents', [])

    # get the events from the database
    events = mongo.db.events.find({"_id": {"$in": joinedEventsIds}})

    return render_template('manage_artworks.html', tmpFileStorage = app.config["UPLOAD_FOLDER"], mongo = mongo, events = events)