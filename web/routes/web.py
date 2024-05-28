from flask import Blueprint, render_template
from flask_login import login_required, current_user

from web.models.ApiKey import ApiKey

web_bp = Blueprint('web', __name__)

@web_bp.route("/")
@web_bp.route("/index")
def index():
    return render_template("index.html")

@web_bp.route("/create")
@login_required
def create():
    return render_template("create_set.html")

@web_bp.route("/keys")
@login_required
def keys():
    keys = ApiKey.query.filter_by(user_id=current_user.id).all()
    key_dict = {key.service: key for key in keys}
    
    openai_key = key_dict.get('OpenAI')
    elevenlabs_key = key_dict.get('ElevenLabs')

    return render_template("keys.html", openai_key=openai_key, elevenlabs_key=elevenlabs_key)