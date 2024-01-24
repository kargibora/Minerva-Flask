from app import app, mongo
from flask import render_template, request, redirect, url_for, session
from utils.date import parse_date

@app.route("/")
def index():
    page = request.args.get('page', default=1, type=int)
    
    # make sure that page > 0
    if page < 1:
        page = 1

    per_page = 6  # posts per page
    start = (page - 1) * per_page
    end = start + per_page

    prompt = request.args.get("prompt") 

    # Get all posts and count total number of pages
    
    posts = mongo.db.posts.find()

    posts_ = list(posts)
    posts_.sort(key=parse_date, reverse=True)
    total_pages = -(-len(posts_) // per_page)  # round up division
    # only get posts for this page
    
    post_list = []
    for i,post in enumerate(posts_):
        if i < start:
            continue
        if i >= end:
            break

        artwork = mongo.db.artworks.find_one({"_id": post["artworkId"]})

        # If a prompt is specified, only include posts that match the prompt
        if prompt:
            if prompt.lower() not in artwork["generativeCaption"].lower():
                continue
        
        user = mongo.db.profile_info.find_one({"username": post["owner"]})
        post_list.append({
            "post": post,
            "artwork": artwork,
            "user": user
        })


    # Pass page info to template
    return render_template('index.html', posts=post_list, page=page, total_pages=total_pages, section_name="For You")


@app.route("/following")
def index_following():
    page = request.args.get('page', default=1, type=int)

    # make sure that page > 0
    if page < 1:
        page = 1

    per_page = 6  # posts per page
    start = (page - 1) * per_page
    end = start + per_page

    prompt = request.args.get("prompt") 

    # Get all posts and count total number of pages
    
    posts = mongo.db.posts.find().sort([("datePosted", -1)])

    posts_ = list(posts)
    total_pages = -(-len(posts_) // per_page)  # round up division
    # only get posts for this page

    #Get the followers of the current user
    current_user = session.get("username")
    current_user_following = []
    if current_user:
        current_user_following = mongo.db.users.find_one({"username": current_user})["following"]

    post_list = []
    for i,post in enumerate(posts_):
        if i < start:
            continue
        if i >= end:
            break

        artwork = mongo.db.artworks.find_one({"_id": post["artworkId"]})

        # If a prompt is specified, only include posts that match the prompt
        if prompt:
            if prompt.lower() not in artwork["generativeCaption"].lower():
                continue
        

        user = mongo.db.profile_info.find_one({"username": post["owner"]})

        # If the post does not belong to a user that the current user is following
        if user["username"] not in current_user_following:
            continue 

        post_list.append({
            "post": post,
            "artwork": artwork,
            "user": user
        })


    # Pass page info to template
    return render_template('index.html', posts=post_list, page=page, total_pages=total_pages, section_name="Following")



@app.route("/search")
def search():
    prompt = request.args.get("prompt")
    if prompt is None:
        return redirect(url_for('index'))

    posts = mongo.db.posts.find().sort([("datePosted", -1)])
    posts_ = list(posts)
    posts_.sort(key=parse_date, reverse=True)
    post_list = []
    for post in posts_:
        artwork = mongo.db.artworks.find_one({"_id": post["artworkId"]})
        if prompt.lower() in artwork["generativeCaption"].lower():
            user = mongo.db.profile_info.find_one({"username": post["owner"]})
            post_list.append({
                "post": post,
                "artwork": artwork,
                "user": user
            })

    return render_template('index.html', posts=post_list)