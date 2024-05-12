from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from web import db
from web.models.ApiKey import ApiKey

api_keys = Blueprint('api_keys', __name__)

@api_keys.route('/update-api-key', methods=['POST'])
@login_required
def update_api_key():
    data = request.get_json()
    service = data['service']
    api_key = data['apiKey']
    
    key_instance = ApiKey.query.filter_by(user_id=current_user.id, service=service).first()
    if not key_instance:
        key_instance = ApiKey(user_id=current_user.id, service=service)
        db.session.add(key_instance)
    
    key_instance.api_key = api_key
    key_instance.last_updated = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'API Key updated successfully'})

@login_required
def get_user_api_key(service):
    possible_services = ['OpenAI', 'ElevenLabs']
    if service not in possible_services:
        raise ValueError(f"Service {service} not supported. Choose from {possible_services}")
    else:
        key_instance = ApiKey.query.filter_by(user_id=current_user.id, service=service).first()
    return key_instance.api_key if key_instance else None

@login_required
def get_openai_api_key():
    return get_user_api_key('OpenAI')

@login_required
def get_elevenlabs_api_key():
    return get_user_api_key('ElevenLabs')
