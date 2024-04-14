from flask import Blueprint, render_template
from flask_login import login_required, current_user

from web.models.ApiKey import ApiKey

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/create")
def create():
    return render_template("create_set.html")

@main_bp.route("/keys")
@login_required
def keys():
    keys = ApiKey.query.filter_by(user_id=current_user.id).all()
    key_dict = {key.service: key for key in keys}
    
    openai_key = key_dict.get('OpenAI')
    elevenlabs_key = key_dict.get('ElevenLabs')

    return render_template("keys.html", openai_key=openai_key, elevenlabs_key=elevenlabs_key)