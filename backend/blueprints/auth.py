from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from bson import ObjectId
auth_bp=Blueprint("auth",__name__)
def _pub(u): return {"id":str(u.get("_id")),"username":u.get("username"),"role":u.get("role","individual"),"points":u.get("points",0)}
@auth_bp.post("/register")
def register():
    d=request.get_json(force=True); u=d.get("username","").strip().lower(); p=d.get("password",""); r=d.get("role","individual")
    if not u or not p: return jsonify(error="username and password required"),400
    if r not in ["individual","business","government"]: r="individual"
    db=current_app.db
    if db.users.find_one({"username":u}): return jsonify(error="username exists"),409
    user={"username":u,"password":generate_password_hash(p),"role":r,"points":0}; db.users.insert_one(user)
    t=create_access_token(identity=str(user["_id"]), additional_claims={"role":r,"username":u})
    return jsonify(token=t, user=_pub(user))
@auth_bp.post("/login")
def login():
    d=request.get_json(force=True); u=d.get("username","").strip().lower(); p=d.get("password","")
    db=current_app.db; user=db.users.find_one({"username":u})
    if not user or not check_password_hash(user["password"], p): return jsonify(error="invalid credentials"),401
    t=create_access_token(identity=str(user["_id"]), additional_claims={"role":user["role"],"username":u})
    return jsonify(token=t, user=_pub(user))
@auth_bp.get("/me")
@jwt_required()
def me():
    claims=get_jwt(); db=current_app.db; user=db.users.find_one({"_id":ObjectId(claims["sub"])}) 
    return jsonify(user=_pub(user))