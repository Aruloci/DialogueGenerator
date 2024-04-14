from web import db
from datetime import datetime, timezone

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service = db.Column(db.String(100))
    api_key = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.now(timezone.utc))
