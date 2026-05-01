from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from backend.config import Config
from backend.models import db, School, DiningHall
from backend.extensions import limiter
from backend.routes.schools import schools_bp
from backend.routes.menu import menu_bp
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    Migrate(app, db)
    CORS(app)
    limiter.init_app(app)

    app.register_blueprint(schools_bp, url_prefix="/api")
    app.register_blueprint(menu_bp, url_prefix="/api")

    @app.errorhandler(429)
    def rate_limit_error(e):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    _register_cli(app)

    return app


def _register_cli(app):
    @app.cli.command("seed")
    def seed():
        """Populate School and DiningHall tables from scraper config."""
        from src.scraper import UHMenuScraper
        scraper = UHMenuScraper()

        for key, cfg in scraper.schools.items():
            school = School.query.filter_by(key=key).first()
            if not school:
                school = School(
                    key=key,
                    name=cfg["name"],
                    domain=cfg["domain"],
                    slug=cfg["slug"],
                    disabled=cfg.get("disabled", False),
                )
                db.session.add(school)
                db.session.flush()
                print(f"  + School: {key}")
            else:
                school.name = cfg["name"]
                school.domain = cfg["domain"]
                school.slug = cfg["slug"]
                school.disabled = cfg.get("disabled", False)

            for short_key, hall_slug in cfg["halls"].items():
                hall = DiningHall.query.filter_by(school_id=school.id, short_key=short_key).first()
                if not hall:
                    db.session.add(DiningHall(
                        school_id=school.id,
                        short_key=short_key,
                        hall_slug=hall_slug,
                    ))
                    print(f"      + Hall: {short_key} → {hall_slug}")
                else:
                    hall.hall_slug = hall_slug

        db.session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
