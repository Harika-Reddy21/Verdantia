from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.external import get_weather, get_soil, get_ndvi
from services.ai import restoration_plan
restore_bp=Blueprint("restore",__name__)
@restore_bp.post("/restore-plan")
@jwt_required()
def plan():
    d=request.get_json(force=True); lat=float(d.get("lat")); lon=float(d.get("lon")); soil_in=d.get("soil") or {}
    soil=get_soil(lat,lon); soil.update(soil_in); climate=get_weather(lat,lon); ndvi=get_ndvi(lat,lon)
    return jsonify(input={"lat":lat,"lon":lon,"soil":soil,"ndvi":ndvi,"climate":climate}, plan=restoration_plan(soil, ndvi, climate))