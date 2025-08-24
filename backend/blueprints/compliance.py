from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt
from utils.roles import roles_required
from services.ai import compliance_eval
from bson import ObjectId
import os, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
comp_bp=Blueprint("comp",__name__)
def _ensure_cert_dir():
    d=os.getenv("CERTIFICATES_DIR","certificates"); os.makedirs(d, exist_ok=True); return d
@comp_bp.post("/compliance-check")
@jwt_required()
def check():
    d=request.get_json(force=True); name=d.get("project_name","Untitled"); area=float(d.get("area_sqm")); trees=int(d.get("trees_planned",0)); green=d.get("green_area_sqm"); green=float(green) if green is not None else None
    res=compliance_eval(area, trees, green); uid=get_jwt()["sub"]
    doc={"user_id":uid,"project_name":name,"area_sqm":area,"trees_planned":trees,"green_area_sqm":green,"result":res,"status":"Submitted","created_at":datetime.utcnow()}
    current_app.db.compliance_reports.insert_one(doc)
    return jsonify(report_id=str(doc.get("_id")), **res)
@comp_bp.get("/compliance-reports")
@jwt_required()
def mine():
    uid=get_jwt()["sub"]; out=[]
    for r in current_app.db.compliance_reports.find({"user_id":uid}).sort("_id",-1):
        r["id"]=str(r.pop("_id")); out.append(r)
    return jsonify(reports=out)
@comp_bp.get("/admin/compliance-pending")
@roles_required("government")
def pending():
    out=[]; 
    for r in current_app.db.compliance_reports.find({"status":{"$ne":"Approved"}}).sort("_id",-1):
        r["id"]=str(r.pop("_id")); out.append(r)
    return jsonify(reports=out)
@comp_bp.put("/compliance-approve/<rid>")
@roles_required("government")
def approve(rid):
    db=current_app.db; doc=db.compliance_reports.find_one({"_id":ObjectId(rid)})
    if not doc: return jsonify(error="not found"),404
    db.compliance_reports.update_one({"_id":ObjectId(rid)},{"$set":{"status":"Approved","approved_at":datetime.utcnow()}})
    cert_dir=_ensure_cert_dir(); path=os.path.join(cert_dir, f"certificate_{rid}.pdf")
    packet=io.BytesIO(); c=canvas.Canvas(packet, pagesize=A4); W,H=A4
    c.setTitle("Green Compliance Certificate"); c.setFont("Helvetica-Bold",20); c.drawCentredString(W/2,H-100,"Green Compliance Certificate")
    c.setFont("Helvetica",12); y=H-150
    def line(t): 
        nonlocal y; c.drawString(72,y,t); y-=18
    line(f"Project: {doc.get('project_name')}"); line(f"Report ID: {rid}"); line(f"Area (sqm): {doc.get('area_sqm')}"); line(f"Trees Planned: {doc.get('trees_planned')}")
    if doc.get('green_area_sqm') is not None: line(f"Green Area (sqm): {doc.get('green_area_sqm')}")
    res=doc.get('result',{}); line(f"Required Trees: {res.get('required_trees')}"); line(f"Required Cover: {res.get('required_cover_pct')}%"); line("Status: Approved")
    from datetime import datetime as dt; line(f"Issued: {dt.utcnow().isoformat()}Z")
    c.setFont("Helvetica-Oblique",10); c.drawString(72,120,"Issued by Verdantia Compliance Engine – for regulatory review."); c.showPage(); c.save()
    open(path,"wb").write(packet.getvalue()); db.compliance_reports.update_one({"_id":ObjectId(rid)},{"$set":{"certificate_path":path}})
    return jsonify(id=rid, status="Approved", certificate=f"/api/compliance-certificate/{rid}")
@comp_bp.get("/compliance-certificate/<rid>")
@roles_required("business","government","individual")
def cert(rid):
    db=current_app.db; doc=db.compliance_reports.find_one({"_id":ObjectId(rid)})
    if not doc or not doc.get("certificate_path"): return jsonify(error="certificate not found"),404
    return send_file(doc["certificate_path"], as_attachment=True)