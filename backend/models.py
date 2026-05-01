from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

VALID_MEAL_TYPES = {"breakfast", "lunch", "dinner", "everyday"}


class School(db.Model):
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)

    halls = db.relationship("DiningHall", backref="school", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "key": self.key,
            "name": self.name,
            "domain": self.domain,
            "slug": self.slug,
            "disabled": self.disabled,
            "halls": [h.to_dict() for h in self.halls],
        }


class DiningHall(db.Model):
    __tablename__ = "dining_halls"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), nullable=False)
    short_key = db.Column(db.String(100), nullable=False)
    hall_slug = db.Column(db.String(200), nullable=False)

    __table_args__ = (db.UniqueConstraint("school_id", "short_key", name="uq_hall_school_key"),)

    items = db.relationship("MenuItem", backref="hall", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "short_key": self.short_key,
            "hall_slug": self.hall_slug,
        }


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey("dining_halls.id"), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    serving_size = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    sugar = db.Column(db.Integer)
    protein_per_calorie = db.Column(db.Float)
    calories_per_protein = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint("hall_id", "meal_type", "date", "name", name="uq_menu_item"),
    )

    def to_dict(self):
        return {
            "name": self.name,
            "serving_size": self.serving_size,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fats": self.fats,
            "sugar": self.sugar,
            "protein_per_calorie": self.protein_per_calorie,
            "calories_per_protein": self.calories_per_protein,
        }
