from app import app, mongo
from flask import render_template, request, redirect, url_for, session
from bson.objectid import ObjectId

@app.route('/p/<post_id>')
def post_page(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    artwork = mongo.db.artworks.find_one({"_id": post["artworkId"]})
    user = mongo.db.profile_info.find_one({"username": post["owner"]})
    # update view count
    mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'viewCount': 1}})
    return render_template('post.html', post=post, artwork=artwork, user=user, mongo=mongo)


