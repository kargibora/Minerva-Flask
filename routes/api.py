from app import app, login_required, mongo, allowed_file, upload_to_s3, s3_client, S3_BUCKET
from datetime import datetime
from flask import jsonify, request, session, send_file, url_for, redirect
from bson import ObjectId, json_util
from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError
import uuid
import os
import io
from PIL import Image, ImageEnhance, ImageFilter, ImageChops
import cv2
import numpy as np

def rotate_hue(img, angle):
    """
    Rotate the hue of an image.
    img: should be an OpenCV BGR image
    angle: the angle to rotate the hue. Can be negative.
    """
    # Convert BGR image to HSV
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(float)

    # Adjust hue
    img_hsv[:, :, 0] = (img_hsv[:, :, 0] + angle) % 180

    # Convert HSV image back to BGR
    img_rotated = cv2.cvtColor(np.uint8(img_hsv), cv2.COLOR_HSV2BGR)

    return img_rotated

def apply_effects(image, hue, saturation, brightness, contrast, blur, sepia, invert):
    # Convert the PIL Image to an OpenCV image
    opencv_image = np.array(image.convert('RGB')) 

    # Reverse RGB to BGR
    opencv_image = opencv_image[:, :, ::-1].copy()

    # Apply hue adjustment
    opencv_image = rotate_hue(opencv_image, hue * 3.6)  # max hue is 360

    # Convert the OpenCV image back to a PIL Image
    # Reverse BGR to RGB
    image = Image.fromarray(opencv_image[:, :, ::-1])

    # Apply saturation adjustment
    converter = ImageEnhance.Color(image)
    image = converter.enhance(saturation / 50)  # Saturation slider goes from 0-100. Normalize to 0-2 range.

    # Apply brightness adjustment
    converter = ImageEnhance.Brightness(image)
    image = converter.enhance(brightness / 50)  # Brightness slider goes from 0-100. Normalize to 0-2 range.

    # Apply contrast adjustment
    converter = ImageEnhance.Contrast(image)
    image = converter.enhance(contrast / 100)  # Contrast slider goes from 0-200. Normalize to 0-2 range.

    # Apply blur adjustment
    image = image.filter(ImageFilter.GaussianBlur(radius=blur))  # Blur slider goes from 0-10

    # Apply sepia filter
    if sepia > 0:  # Sepia slider goes from 0-100
        sepia_image = Image.new('RGB', image.size, (112, 66, 20))  # Create sepia layer
        image = Image.blend(image, sepia_image, sepia / 100)  # Blend based on sepia amount

    # Apply invert adjustment
    if invert > 0:  # Invert slider goes from 0-100
        image = ImageChops.invert(image)
        inverted_image = Image.new('RGB', image.size, (255, 255, 255))
        image = Image.blend(image, inverted_image, invert / 100)  # Blend based on invert amount

    return image

@app.route('/v1/api/like/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    username = session['username']
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if username in post["likes"]:
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)},
                {
                    "$pull": {
                        "likes": username
                    },
                    "$inc": {
                        "likeCount": -1
                    }
                }
            )
        mongo.db.users.update_one(
            {"username": username},
            {
                "$pull": {
                    "likedPosts": post_id
                }
            }
        )
        return jsonify({"success": True, "liked": False })
    else:
        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$push": {
                    "likes": username
                },
                "$inc": {
                    "likeCount": 1
                }
            }
        )
        mongo.db.users.update_one(
            {"username": username},
            {
                "$push": {
                    "likedPosts": post_id
                }
            }
        )
        return jsonify({"success": True, "liked": True })
    
@app.route('/v1/api/event/like/<post_id>', methods=['POST'])
@login_required
def like_post_event(post_id):
    username = session['username']
    post = mongo.db.event_posts.find_one({"_id": ObjectId(post_id)})
    if username in post["likes"]:
        mongo.db.event_posts.update_one(
            {"_id": ObjectId(post_id)},
                {
                    "$pull": {
                        "likes": username
                    },
                    "$inc": {
                        "likeCount": -1
                    }
                }
            )
        mongo.db.users.update_one(
            {"username": username},
            {
                "$pull": {
                    "likedPosts": post_id
                }
            }
        )
        return jsonify({"success": True, "liked": False })
    else:
        mongo.db.event_posts.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$push": {
                    "likes": username
                },
                "$inc": {
                    "likeCount": 1
                }
            }
        )
        mongo.db.users.update_one(
            {"username": username},
            {
                "$push": {
                    "likedPosts": post_id
                }
            }
        )
        return jsonify({"success": True, "liked": True })

@app.route('/v1/api/comment/<post_id>', methods=['POST'])
@login_required
def comment(post_id):
    username = session['username']
    text = request.json['text']

    if not text:
        return jsonify({'success': False, 'message': 'Empty comment'})

    user = mongo.db.users.find_one({'username': username})
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    comment_data = {
        'username': user['username'],
        'text': text,
        'createdAt': dt_string,
    }

    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                f"comments.{uuid.uuid4().hex}": comment_data
            },
            "$inc": {
                "commentCount": 1
            }
        }
    )

    return jsonify({'success': True})

@app.route('/v1/api/event/comment/<post_id>', methods=['POST'])
@login_required
def comment_event(post_id):
    username = session['username']
    text = request.json['text']

    if not text:
        return jsonify({'success': False, 'message': 'Empty comment'})

    user = mongo.db.users.find_one({'username': username})
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    comment_data = {
        'username': user['username'],
        'text': text,
        'createdAt': dt_string,
    }

    mongo.db.event_posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                f"comments.{uuid.uuid4().hex}": comment_data
            },
            "$inc": {
                "commentCount": 1
            }
        }
    )

    return jsonify({'success': True})

@app.route('/v1/api/get-artworks/<username>')
@login_required
def get_artworks(username):
    artworks = mongo.db.artworks.find({"owner": username})
    artworks_json = json_util.dumps(artworks)  # Convert the artworks to JSON
    return artworks_json

@app.route('/v1/api/delete-comment/<post_id>/<comment_id>', methods=['POST'])
@login_required
def delete_comment(post_id, comment_id):
    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$unset": {
                f"comments.{comment_id}": ""
            },
            "$inc": {
                "commentCount": -1
            }
        }
    )
    return jsonify({'success': True})

@app.route('/v1/api/event/delete-comment/<post_id>/<comment_id>', methods=['POST'])
@login_required
def delete_comment_event(post_id, comment_id):
    mongo.db.event_posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$unset": {
                f"comments.{comment_id}": ""
            },
            "$inc": {
                "commentCount": -1
            }
        }
    )
    return jsonify({'success': True})

@app.route('/v1/api/delete-post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):

    # check if the post is owned by the user in the session
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    
    # if post is not found, search in the user's posts
    if not post:
        post = mongo.db.event_posts.find_one({"_id": ObjectId(post_id)})

    if post['owner'] != session['username']:
        return jsonify({'success': False, 'message': 'You are not authorized to delete this post'}), 403

    # delete the post from the database
    mongo.db.posts.delete_one({"_id": ObjectId(post_id)})

    # deleting post also should delete it from users.posts
    mongo.db.users.update_one(
        {"username": session['username']},
        {
            "$pull": {
                "posts": ObjectId(post_id)
            }
        }
    )

    # delete the post from all user's liked posts
    mongo.db.users.update_many(
        {},
        {
            "$pull": {
                "likedPosts": ObjectId(post_id)
            }
        }
    )

    # redirect to the main page with a alert message
    return redirect(url_for('index', alert_message='Post deleted successfully'))


@app.route('/v1/api/edit-caption/<post_id>', methods=['POST'])
def edit_caption(post_id):
    caption = request.json['caption']
    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {
            "$set": {
                "caption": caption
            }
        }
    )
    return jsonify({'success': True})
    

@app.route('/v1/api/delete-artwork/<artwork_id>', methods=['POST'])
@login_required
def delete_artwork(artwork_id):
    print(artwork_id)
    mongo.db.artworks.delete_one({"_id": ObjectId(artwork_id)})

    # # deleting artwork also should delete it from users.artworks
    mongo.db.users.update_one(
        {"username": session['username']},
        {
            "$pull": {
                "artworks": ObjectId(artwork_id)
            }
        }
    )

    # # send request to delete-post to delete the posts associated with this artwork
    posts = mongo.db.posts.find({"artworkId": ObjectId(artwork_id)})
    print(posts)
    for post in posts:
        delete_post(post['_id'])

    return jsonify({'success': True})



@app.route('/v1/api/follow/<username>', methods=['POST'])
@login_required
def follow_user(username):
    mongo.db.users.update_one(
        {"username": session['username']},
        {
            "$push": {
                "following": username
            }
        }
    )

    mongo.db.users.update_one(
        {"username": username},
        {
            "$push": {
                "followers": session['username']
            }
        }
    )

    return jsonify({'success': True})

@app.route('/v1/api/unfollow/<username>', methods=['POST'])
@login_required
def unfollow_user(username):
    mongo.db.users.update_one(
        {"username": session['username']},
        {
            "$pull": {
                "following": username
            }
        }
    )

    mongo.db.users.update_one(
        {"username": username},
        {
            "$pull": {
                "followers": session['username']
            }
        }
    )

    return jsonify({'success': True})

@app.route('/v1/api/likes/<post_id>', methods=['GET'])
def get_likes(post_id):
    curr_user = mongo.db.users.find_one({"username": session['username']})
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    liked_by = []
    for username in post['likes']:
        profile = mongo.db.profile_info.find_one({"username": username})
        user = mongo.db.users.find_one({"username": username})
        print(post['owner'] in user['following'])
        print("post owner: ", post['owner'])
        print("user following: ", user['following'])
        liked_by.append({'fullname': profile['name'] + " " + profile['surname'], 'username': profile['username'], 'profilePictureS3URL': profile['profilePictureS3URL'], 'isFollowing': username in curr_user['following']})

    return jsonify(liked_by)

@app.route('/v1/api/event/likes/<post_id>', methods=['GET'])
def get_likes_event(post_id):
    curr_user = mongo.db.users.find_one({"username": session['username']})
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    liked_by = []
    for username in post['likes']:
        profile = mongo.db.profile_info.find_one({"username": username})
        user = mongo.db.users.find_one({"username": username})
        print(post['owner'] in user['following'])
        print("post owner: ", post['owner'])
        print("user following: ", user['following'])
        liked_by.append({'fullname': profile['name'] + " " + profile['surname'], 'username': profile['username'], 'profilePictureS3URL': profile['profilePictureS3URL'], 'isFollowing': username in curr_user['following']})

    return jsonify(liked_by)

@app.route('/v1/api/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    # get the file 
    file = request.files['file']

    # get meta parameters if provided
    text_prompt = request.form.get('promptTxt','')
    username = request.form.get('username','')

    # get meta parameters
    negative_prompt = request.form.get('negativePromptTxt','')
    model_name = request.form.get('modelName','')
    model_guidance_scale = request.form.get('guidanceScale','')
    model_num_steps = request.form.get('numSteps','')
    scheduler_name = request.form.get('schedulerName','')
    seed = request.form.get('seed','')
    model_image_size = request.form.get('imageSize','')

    print(request.form)


    if username == '':
        username = session.get('username','')

        if username == '':
            return jsonify({"error": "No username provided"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Supported file types are: .jpg, .jpeg, .png"}), 400

    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"
    secure_name = secure_filename(unique_filename)

    # upload image to s3 bucket
    file_url = upload_to_s3(S3_BUCKET, s3_client, file=file)
    if file_url is None:
        return jsonify({"error": "An error occurred while uploading the image. Please try again."}), 500

    # upload the image to mongo db with correct credentials
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    artwork = mongo.db.artworks.insert_one({
        "owner": username,
        "imageURLS3": file_url,
        "dateGenerated": dt_string,
        "generativeCaption" : text_prompt,
        "negativePrompt" : negative_prompt,
        "modelName" : model_name,
        "guidanceScale" : float(model_guidance_scale),
        "numSteps" : int(model_num_steps),
        "schedulerName" : scheduler_name,
        "seed" : int(seed),
        "imageSize" : int(model_image_size)
    })

    # also insert this post information into the user's posts
    mongo.db.users.update_one(
        {"username": username},
        {
            "$push": {
                "artworks": artwork.inserted_id,
            }
        }
    )

    return jsonify({"success": True, "file_url": file_url}), 201

@app.route('/v1/api/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():

    # check whether request is valid or not by comparing which user is logged in
    # if username != session['username']:
    #     return jsonify({"error": "Invalid request"}), 400

    if 'image' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    # get the file 
    file = request.files['image']

    file_url = upload_to_s3(S3_BUCKET, s3_client, file=file)
    # update the mongo db with the new profile picture
    mongo.db.profile_info.update_one(
        {"username": session['username']},
        {
            "$set": {
                "profilePictureS3URL": file_url
            }
        }
    )

    return jsonify({"success": True, "file_url": file_url}), 201

@app.route('/v1/api/get-image-file', methods=['POST'])
def get_image_file():
    image_url = request.json['url']

    # check if url is an s3 url
    if not image_url.startswith("https://") and "S3" not in image_url:
        return jsonify({"error": "Invalid S3"}), 400
    elif image_url.startswith("https://") and "S3" in image_url:
        try:
            # Extract the file name from the url
            file_name = image_url.split("/")[-1]
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            # Download the file from S3 to the local filesystem
            s3_client.download_file(S3_BUCKET, file_name, save_path)

            # Send the file as a response
            return send_file(save_path, as_attachment=True)

        finally:
            if os.path.exists(save_path):
                os.remove(save_path)  # Clean up the file from local filesystem
    else: # url is in the local filesystem
        try:
            return send_file(image_url, as_attachment=True)
        finally:
            if os.path.exists(image_url):
                os.remove(image_url)

@app.route('/v1/api/share-post', methods=['POST'])
def share_post():
    # get user from session
    username = session['username']

    # handle the POST request
    description = request.json.get('description', "")
    image_id = request.json.get('image_id', None)
    if image_id is None:
        return jsonify({'success': False, 'message': 'No valid image is provided'})
    
    # convert image id to ObjectId
    image_id = ObjectId(image_id["$oid"])

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    post = mongo.db.posts.insert_one({
        'owner': username,
        'caption': description,
        'artworkId': image_id,
        'likes': [],
        'comments': {},
        'likeCount': 0,
        'commentCount': 0,
        'viewCount': 0,
        'datePosted': dt_string
    })

    # also insert this post information into the user's posts
    mongo.db.users.update_one(
        {"username": username},
        {
            "$push": {
                "posts": post.inserted_id,
            }
        }
    )

    return jsonify({'success': True, 'message': 'Post shared successfully'}), 201

@app.route('/v1/api/share-post/event', methods=['POST'])
def share_post_event():
    # get user from session
    username = session['username']

    # handle the POST request
    description = request.json.get('description', "")
    image_id = request.json.get('image_id', None)
    event_id = request.json.get('event_id', None)

    if image_id is None:
        return jsonify({'success': False, 'message': 'No valid image is provided'})
    
    if event_id is None:
        return jsonify({'success': False, 'message': 'No valid event is provided'})
    
    # convert image id to ObjectId
    image_id = ObjectId(image_id["$oid"])

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


    post = mongo.db.event_posts.insert_one({
        'owner': username,
        'caption': description,
        'artworkId': image_id,
        'likes': [],
        'retweets': [],
        'comments': {},
        'likeCount': 0,
        'retweetCount': 0,
        'commentCount': 0,
        'datePosted': dt_string
    })

    # insert the post to the field artworkPosts for the given event with the event id 
    mongo.db.events.update_one(
        {"_id": ObjectId(event_id)},
        {
            "$push": {
                "artworkPosts": post.inserted_id,
            },
            "$inc": {
                "postedArtworkCount": 1
            }, # also set lastPostedBy and lastPostedAt fields
            "$set": {
                "lastPostedBy": username,
                "lastPostedAt": dt_string
            }
        }
    )

    return jsonify({'success': True, 'message': 'Post shared successfully'}), 201

@app.route('/v1/api/load-parameters/<artwork_id>', methods=['GET'])
def load_parameters(artwork_id):
    # Retrieve the artwork from MongoDB using the artwork_id
    artwork = mongo.db.artworks.find_one({"_id": ObjectId(artwork_id)})
    
    if not artwork:
        return jsonify({"error": "Artwork not found"}), 404

    # Extract the parameters
    parameters = {
        "text_prompt": artwork.get("generativeCaption", ""),
        "negative_prompt": artwork.get("negativePrompt", ""),
        "model_name": artwork.get("modelName", ""),
        "model_guidance_scale": artwork.get("guidanceScale", ""),
        "model_num_steps": artwork.get("numSteps", ""),
        "scheduler_name": artwork.get("schedulerName", ""),
        "seed": artwork.get("seed", ""),
        "model_image_size": artwork.get("imageSize", ""),
        "image_url": artwork.get("imageURLS3", ""),
    }

    return jsonify(parameters)

@app.route('/v1/api/search-username/<username>', methods=['GET'])
def search_username(username):
    regex = '^' + username  # Starts with 'username'
    cursor = mongo.db.profile_info.find({"username": {"$regex": regex}}).limit(10) # Get users where username starts with the input
    users_list = []
    for document in cursor:
        document['_id'] = str(document['_id'])  # Convert ObjectId() to string
        users_list.append(document)
    return jsonify(users_list), 200


@app.route('/download/<artwork_id>')
def download(artwork_id):
    # get the artwork object
    artwork = mongo.db.artworks.find_one({"_id": ObjectId(artwork_id)})
    s3Url = artwork['imageURLS3']
    filename = s3Url.split("/")[-1]
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
        img_data = obj['Body'].read()
        return send_file(io.BytesIO(img_data), mimetype='image/jpeg', as_attachment=True, download_name=filename)
    except NoCredentialsError:
        return {'error': 'S3 Access Denied'}, 403


@app.route('/v1/api/save-effects/<artwork_id>', methods=['POST'])
def save_effects(artwork_id):

    # Get the artwork object
    artwork = mongo.db.artworks.find_one({"_id": ObjectId(artwork_id)})
    
    # Load the image from S3
    s3Url = artwork['imageURLS3']
    filename = s3Url.split("/")[-1]
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
        img_data = obj['Body'].read()
        img = Image.open(io.BytesIO(img_data))
    except NoCredentialsError:
        return {'error': 'S3 Access Denied'}, 403
    # Get the effect values from the request
    data = request.get_json()
    saturation = float(data.get('saturation', 1))
    hue = float(data.get('hue', 0))
    brightness = float(data.get('brightness', 1))
    contrast = float(data.get('contrast', 1))
    blur = float(data.get('blur', 0))
    sepia = float(data.get('sepia', 0))
    invert = float(data.get('invert', 0))

    # Apply the effects using PIL's ImageEnhance module
    img = apply_effects(img, hue, saturation, brightness, contrast, blur, sepia, invert)

    # Modify the filename so its unique by adding a timestamp
    filename = filename.split(".")[0] + f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpeg"
    # Upload the image to s3
    file_bytes = io.BytesIO()
    img.save(file_bytes, format='JPEG')
    file_bytes = file_bytes.getvalue()

    file_url = upload_to_s3(S3_BUCKET, s3_client, file_type='image/jpeg', file_name=filename, file_byte=file_bytes)

    # Create the artwork object in MongoDB
    mongo.db.artworks.insert_one({
        "owner": session['username'],
        "imageURLS3": file_url,
        "dateGenerated": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "generativeCaption" : artwork.get("generativeCaption", ""),
        "negativePrompt" : artwork.get("negativePrompt", ""),
        "modelName" : artwork.get("modelName", ""),
        "guidanceScale" : artwork.get("guidanceScale", ""),
        "numSteps" : artwork.get("numSteps", ""),
        "schedulerName" : artwork.get("schedulerName", ""),
        "seed" : artwork.get("seed", ""),
        "imageSize" : artwork.get("imageSize", ""),
        "parentArtworkId": artwork_id
    })

    return jsonify({"success": True, "file_url": file_url}), 201

