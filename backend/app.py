import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from pymongo import MongoClient
from blueprints.auth import auth_bp
from blueprints.recommendation import reco_bp
from blueprints.compliance import comp_bp
from blueprints.permissions import perm_bp
from blueprints.gamification import game_bp
from blueprints.restore import restore_bp
def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"]=os.getenv("SECRET_KEY","x")
    app.config["JWT_SECRET_KEY"]=os.getenv("JWT_SECRET_KEY","y")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"]=timedelta(days=1)
    CORS(app, resources={r"/api/*":{"origins":os.getenv("ALLOWED_ORIGINS","http://localhost:5173").split(",")}}, supports_credentials=True)
    mongo_uri=os.getenv("MONGO_URI","mongodb://localhost:27017/verdantia")
    client=MongoClient(mongo_uri); db_name=mongo_uri.rsplit("/",1)[-1]
    app.db=client[db_name]
    JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(reco_bp, url_prefix="/api")
    app.register_blueprint(comp_bp, url_prefix="/api")
    app.register_blueprint(perm_bp, url_prefix="/api")
    app.register_blueprint(game_bp, url_prefix="/api")
    app.register_blueprint(restore_bp, url_prefix="/api")
    @app.route("/api/health")
    def health(): return jsonify(status="ok")
    return app
if __name__=="__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)