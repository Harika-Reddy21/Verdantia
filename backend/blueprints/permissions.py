from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from utils.roles import roles_required
from bson import ObjectId
perm_bp=Blueprint("perm",__name__)
@perm_bp.post("/land-permission")
@jwt_required()
def create():
    uid=get_jwt()["sub"]; d=request.get_json(force=True)
    doc={"applicant_id":uid,"location":d.get("location"),"area_sqm":d.get("area_sqm"),"species_proposed":d.get("species_proposed",[]),"count_proposed":d.get("count_proposed",0),"description":d.get("description",""),"status":"Pending"}
    current_app.db.permissions.insert_one(doc); doc["id"]=str(doc.pop("_id")); return jsonify(permission=doc)
@perm_bp.get("/land-permissions")
@roles_required("government")
def list_all():
    out=[]; 
    for p in current_app.db.permissions.find().sort("_id",-1):
        p["id"]=str(p.pop("_id")); out.append(p)
    return jsonify(permissions=out)
@perm_bp.put("/land-permission/<pid>")
@roles_required("government")
def decide(pid):
    d=request.get_json(force=True); action=d.get("action"); note=d.get("note","")
    status="Approved" if action=='approve' else "Denied"; current_app.db.permissions.update_one({"_id":ObjectId(pid)},{"$set":{"status":status,"decision_note":note}})
    return jsonify(id=pid, status=status, note=note)