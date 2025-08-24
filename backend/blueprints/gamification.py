import os, uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from bson import ObjectId
from services.external import s3_upload_bytes
game_bp=Blueprint("game",__name__)
ALLOWED={"mp4","mov","avi","mkv","jpg","jpeg","png"}
def _ok(fn): return "." in fn and fn.rsplit(".",1)[1].lower() in ALLOWED
@game_bp.post("/upload-video")
@jwt_required()
def upload():
    if "file" not in request.files: return jsonify(error="no file"),400
    f=request.files["file"]
    if f.filename=="" or not _ok(f.filename): return jsonify(error="invalid file"),400
    fname=f"{uuid.uuid4().hex}_{f.filename}"; d=os.getenv("UPLOAD_DIR","uploads"); os.makedirs(d,exist_ok=True); path=os.path.join(d,fname)
    f.save(path); data=open(path,"rb").read(); url=s3_upload_bytes(f"uploads/{fname}", data, content_type=f.mimetype or "application/octet-stream")
    uid=get_jwt()["sub"]; current_app.db.uploads.insert_one({"user_id":uid,"filename":fname,"url":url}); current_app.db.users.update_one({"_id":ObjectId(uid)},{"$inc":{"points":50}})
    return jsonify(filename=fname, url=url, points_awarded=50)
@game_bp.get("/my-videos")
@jwt_required()
def myvids():
    uid=get_jwt()["sub"]; out=[]; 
    for v in current_app.db.uploads.find({"user_id":uid}).sort("_id",-1):
        v["id"]=str(v.pop("_id")); out.append(v)
    return jsonify(videos=out)
@game_bp.get("/leaderboard")
def lb():
    users=current_app.db.users.find({},{"username":1,"points":1}).sort("points",-1).limit(20)
    return jsonify(leaderboard=[{"username":u["username"],"points":u.get("points",0)} for u in users])