import re

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Resource, Api
from app.database import SessionLocal
from app.models import EDL, Entry
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

# ------------------------------
# EDL List (GET, POST)
# ------------------------------
class EDLListResource(Resource):
    def get(self):
        """Return a list of all EDLs."""
        session = SessionLocal()
        edls = session.query(EDL).all()
        session.close()
        return jsonify([{"name": edl.name, "description": edl.description} for edl in edls])

    @jwt_required()
    def post(self):
        """Create a new EDL with validation (same as Web UI)."""
        data = request.get_json()
        current_admin = get_jwt_identity()  # Get username from token

        if not data:
            return make_response(jsonify({"error": "Invalid JSON"}), 400)

        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        # Name Validation
        if len(name) < 4:
            return make_response(jsonify({"error": "EDL name must be at least 4 characters long."}), 400)
        if not any(c.isalpha() for c in name):
            return make_response(jsonify({"error": "EDL name must contain at least one alphabetical character."}), 400)
        if not re.match(r"^[a-zA-Z0-9]+$", name):
            return make_response(jsonify({"error": "EDL name must be alphanumeric with no special characters or spaces."}), 400)

        # Description Validation
        if len(description) > 50:
            return make_response(jsonify({"error": "Description must not exceed 50 characters."}), 400)
        if re.search(r"[<>'\";%&()]", description):
            return make_response(jsonify({"error": "Description contains invalid characters."}), 400)

        session = SessionLocal()
        existing_edl = session.query(EDL).filter_by(name=name).first()

        if existing_edl:
            session.close()
            return make_response(jsonify({"error": "EDL with this name already exists."}), 400)

        new_edl = EDL(name=name, description=description, created_by=current_admin)
        session.add(new_edl)
        session.commit()
        session.close()

        return make_response(jsonify({"message": "EDL created successfully!", "name": name}), 201)

# ------------------------------
# Single EDL (GET, DELETE)
# ------------------------------
class EDLResource(Resource):
    def get(self, edl_name):
        """Retrieve details of a specific EDL"""
        session = SessionLocal()
        edl = session.query(EDL).filter_by(name=edl_name).first()
        session.close()

        if not edl:
            return make_response(jsonify({"error": "EDL not found"}), 404)

        return jsonify({"name": edl.name, "description": edl.description})

    @jwt_required()
    def delete(self, edl_name):
        """Delete an EDL"""
        session = SessionLocal()
        edl = session.query(EDL).filter_by(name=edl_name).first()

        if not edl:
            session.close()
            return make_response(jsonify({"error": "EDL not found"}), 404)

        session.delete(edl)
        session.commit()
        session.close()

        return make_response(jsonify({"message": f"EDL '{edl_name}' deleted successfully"}), 200)

# ------------------------------
# Entries (GET, POST)
# ------------------------------
class EDLEntriesResource(Resource):
    def get(self, edl_name):
        """Retrieve all entries in an EDL"""
        session = SessionLocal()
        edl = session.query(EDL).filter_by(name=edl_name).first()

        if not edl:
            session.close()
            return make_response(jsonify({"error": "EDL not found"}), 404)

        entries = session.query(Entry).filter_by(edl_id=edl.id).all()
        session.close()

        return jsonify([
            {"id": entry.id, "value": entry.value, "description": entry.description, "created_at": str(entry.created_at)}
            for entry in entries
        ])

    @jwt_required()
    def post(self, edl_name):
        """Add an entry to an EDL"""
        data = request.get_json()
        value = data.get("value", "").strip()
        description = data.get("description", "").strip()
        current_admin = get_jwt_identity()  # Get username from token

        session = SessionLocal()
        edl = session.query(EDL).filter_by(name=edl_name).first()

        if not edl:
            session.close()
            return make_response(jsonify({"error": "EDL not found"}), 404)

        new_entry = Entry(edl_id=edl.id, value=value, description=description, created_by=current_admin)
        session.add(new_entry)
        session.commit()
        session.close()

        return make_response(jsonify({"message": "Entry added successfully!", "value": value}), 201)

# ------------------------------
# Single Entry (DELETE)
# ------------------------------
class EntryResource(Resource):
    @jwt_required()
    def delete(self, entry_id):
        """Delete an entry"""
        session = SessionLocal()
        entry = session.query(Entry).filter_by(id=entry_id).first()

        if not entry:
            session.close()
            return make_response(jsonify({"error": "Entry not found"}), 404)

        session.delete(entry)
        session.commit()
        session.close()

        return make_response(jsonify({"message": "Entry deleted successfully!"}), 200)

# ------------------------------
# Register API Endpoints
# ------------------------------
api.add_resource(EDLListResource, "/edls")
api.add_resource(EDLResource, "/edls/<string:edl_name>")
api.add_resource(EDLEntriesResource, "/edls/<string:edl_name>/entries")
api.add_resource(EntryResource, "/entries/<int:entry_id>")
