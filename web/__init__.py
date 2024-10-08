from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from web.config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from web.models.Users import Users
    
    # ROUTES
    from web.routes.auth import auth_bp
    from web.routes.web import web_bp
    from web.routes.api_keys import api_keys
    from web.routes.api import api
    app.register_blueprint(auth_bp)
    app.register_blueprint(web_bp)
    app.register_blueprint(api_keys)
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    return app
