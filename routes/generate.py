from app import app, mongo,login_required
from flask import render_template, request, redirect, url_for, session

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    copyArtworkId = request.args.get("artworkId", None)
    forkedArtworkId = request.args.get("forkedArtworkId", None)
    selectedTab = request.args.get("selectedTab", 0)
    return render_template('generate.html', artworkId = copyArtworkId, selectedTab = selectedTab, forkedArtworkId = forkedArtworkId, mongo = mongo)
