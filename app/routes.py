
import logging

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from app.models import Student, db

students_bp = Blueprint("students", __name__, url_prefix="/api/v1")
logger = logging.getLogger(__name__)


@students_bp.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Request body must be a JSON object"}, 400

    name = data.get("name")
    email = data.get("email")
    age = data.get("age")

    if not isinstance(name, str) or not name.strip():
        return {"error": "Name is required"}, 400

    if not isinstance(email, str) or not email.strip():
        return {"error": "Email is required"}, 400

    if isinstance(age, bool) or not isinstance(age, int) or age < 0:
        return {"error": "Age must be a non-negative integer"}, 400

    student = Student(
        name=name.strip(),
        email=email.strip(),
        age=age,
    )

    try:
        db.session.add(student)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "A student with this email already exists"}, 409

    logger.info("Created student id=%s", student.id)
    return student.to_dict(), 201


@students_bp.route("/students", methods=["GET"])
def list_students():
    students = db.session.execute(
        db.select(Student).order_by(Student.id)
    ).scalars().all()

    return {"students": [student.to_dict() for student in students]}, 200


@students_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return {"error": "Student not found"}, 404

    return student.to_dict(), 200


@students_bp.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return {"error": "Student not found"}, 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Request body must be a JSON object"}, 400

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return {"error": "Name must be a non-empty string"}, 400
        student.name = data["name"].strip()

    if "email" in data:
        if not isinstance(data["email"], str) or not data["email"].strip():
            return {"error": "Email must be a non-empty string"}, 400
        student.email = data["email"].strip()

    if "age" in data:
        age = data["age"]
        if isinstance(age, bool) or not isinstance(age, int) or age < 0:
            return {"error": "Age must be a non-negative integer"}, 400
        student.age = age

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "A student with this email already exists"}, 409

    logger.info("Updated student id=%s", student.id)
    return student.to_dict(), 200


@students_bp.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = db.session.get(Student, student_id)

    if student is None:
        return {"error": "Student not found"}, 404

    db.session.delete(student)
    db.session.commit()

    logger.info("Deleted student id=%s", student_id)
    return {"message": "Student deleted successfully"}, 200

