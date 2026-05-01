from flask import Blueprint, jsonify, request, g
from datetime import date as date_type, datetime
from backend.models import db, School, DiningHall, MenuItem, VALID_MEAL_TYPES
from backend.extensions import limiter
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.scraper import UHMenuScraper

menu_bp = Blueprint("menu", __name__)


def _scrape_and_store(school_key, short_key, meal_type, target_date):
    scraper = UHMenuScraper()
    raw = scraper.get_today_menu(
        find_date=target_date.isoformat(),
        menu_type=meal_type,
        dining_hall=short_key,
        school=school_key,
        refresh_cache=True,
    )

    school = School.query.filter_by(key=school_key).first()
    hall = DiningHall.query.filter_by(school_id=school.id, short_key=short_key).first()

    for row in raw:
        existing = MenuItem.query.filter_by(
            hall_id=hall.id,
            meal_type=meal_type,
            date=target_date,
            name=row["name"],
        ).first()
        if existing:
            continue
        db.session.add(MenuItem(
            hall_id=hall.id,
            meal_type=meal_type,
            date=target_date,
            name=row["name"],
            serving_size=row.get("serving_size"),
            calories=row.get("calories"),
            protein=row.get("protein"),
            carbs=row.get("carbs"),
            fats=row.get("fats"),
            sugar=row.get("sugar"),
            protein_per_calorie=row.get("protein_per_calorie"),
            calories_per_protein=row.get("calories_per_protein"),
        ))
    db.session.commit()

    return MenuItem.query.filter_by(
        hall_id=hall.id, meal_type=meal_type, date=target_date
    ).all()


@menu_bp.route("/menu")
@limiter.limit("15/minute", deduct_when=lambda response: getattr(g, "did_scrape", False))
def get_menu():
    school_key = (request.args.get("school") or "").upper()
    short_key = request.args.get("hall") or ""
    meal_type = (request.args.get("meal") or "").lower()
    date_str = request.args.get("date") or date_type.today().isoformat()

    if not school_key or not short_key or not meal_type:
        return jsonify({"error": "school, hall, and meal are required"}), 400
    if meal_type not in VALID_MEAL_TYPES:
        return jsonify({"error": f"meal must be one of {sorted(VALID_MEAL_TYPES)}"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "date must be YYYY-MM-DD"}), 400

    school = School.query.filter_by(key=school_key).first()
    if not school:
        return jsonify({"error": f"Unknown school: {school_key}"}), 404
    hall = DiningHall.query.filter_by(school_id=school.id, short_key=short_key).first()
    if not hall:
        return jsonify({"error": f"Unknown hall '{short_key}' for {school_key}"}), 404

    items = MenuItem.query.filter_by(
        hall_id=hall.id, meal_type=meal_type, date=target_date
    ).all()

    if not items:
        g.did_scrape = True
        try:
            items = _scrape_and_store(school_key, short_key, meal_type, target_date)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify([i.to_dict() for i in items])


@menu_bp.route("/menu/scrape", methods=["POST"])
@limiter.limit("5/minute")
def force_scrape():
    body = request.get_json(silent=True) or {}
    school_key = (body.get("school") or "").upper()
    short_key = body.get("hall") or ""
    meal_type = (body.get("meal") or "").lower()
    date_str = body.get("date") or date_type.today().isoformat()

    if not school_key or not short_key or not meal_type:
        return jsonify({"error": "school, hall, and meal are required"}), 400
    if meal_type not in VALID_MEAL_TYPES:
        return jsonify({"error": f"meal must be one of {sorted(VALID_MEAL_TYPES)}"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "date must be YYYY-MM-DD"}), 400

    school = School.query.filter_by(key=school_key).first()
    if not school:
        return jsonify({"error": f"Unknown school: {school_key}"}), 404
    hall = DiningHall.query.filter_by(school_id=school.id, short_key=short_key).first()
    if not hall:
        return jsonify({"error": f"Unknown hall '{short_key}' for {school_key}"}), 404

    MenuItem.query.filter_by(
        hall_id=hall.id, meal_type=meal_type, date=target_date
    ).delete()
    db.session.commit()

    try:
        items = _scrape_and_store(school_key, short_key, meal_type, target_date)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([i.to_dict() for i in items])
