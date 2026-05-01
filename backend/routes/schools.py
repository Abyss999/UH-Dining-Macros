from flask import Blueprint, jsonify
from backend.models import School

schools_bp = Blueprint("schools", __name__)


@schools_bp.route("/schools")
def list_schools():
    schools = School.query.filter_by(disabled=False).order_by(School.name).all()
    return jsonify([s.to_dict() for s in schools])


@schools_bp.route("/schools/<key>/halls")
def list_halls(key):
    school = School.query.filter_by(key=key.upper()).first_or_404()
    return jsonify([h.to_dict() for h in school.halls])
