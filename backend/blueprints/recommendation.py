from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.external import get_weather, get_soil, get_ndvi
from services.ai import recommend_species
reco_bp=Blueprint("reco",__name__)
@reco_bp.post("/recommendation")
@jwt_required()
def recommendation():
    d=request.get_json(force=True); lat=float(d.get("lat")); lon=float(d.get("lon")); area=float(d.get("area_sqm",1000))
    w=get_weather(lat,lon); s=get_soil(lat,lon); n=get_ndvi(lat,lon)
    return jsonify(input={"lat":lat,"lon":lon,"area_sqm":area,"ndvi":n,"weather":w,"soil":s}, recommendation=recommend_species(w,s))