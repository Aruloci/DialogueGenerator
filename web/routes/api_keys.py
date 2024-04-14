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