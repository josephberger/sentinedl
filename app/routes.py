import csv
import io
import re
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, Response
from app.database import SessionLocal
from sqlalchemy.orm import joinedload 
from app.models import EDL, Entry
from flask_login import login_required, current_user

# Create a Flask Blueprint for EDL routes
edl_bp = Blueprint("edl", __name__)

def sanitize_description(description):
    """Sanitize input to prevent XSS, SQL injection, and ensure max length."""
    description = description.strip()
    if len(description) > 50:
        return None, "Description must not exceed 50 characters."
    invalid_chars = r"[<>%'();&]"  # Removed double quote from regex, handled separately
    if '"' in description:
        return None, "Description contains invalid characters."
    if re.search(invalid_chars, description):
        return None, "Description contains invalid characters."
    return description, None

def validate_entry_value(value):
    """Validate entry value to ensure it is an IP (IPv4/IPv6), FQDN (with optional wildcard), or URL (without protocol)."""
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}$"
    fqdn_pattern = r"^(\*\.)?(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:[A-Za-z]{2,8})$"
    url_pattern = r"^(\*\.)?([A-Za-z0-9.-]+)\.(?:[A-Za-z]{2,8})(/[\w\-._~:/?#[\]@!$&'()*+,;=]*)?$"
    
    if re.match(ip_pattern, value):
        return value, None
    if re.match(ipv6_pattern, value):
        return value, None
    if re.match(fqdn_pattern, value):
        return value, None
    if re.match(url_pattern, value):
        return value, None
    
    return None, "Entry value must be a valid IPv4, IPv6, FQDN, or URL."

@edl_bp.route("/", methods=["GET"])
def home():
    """Render the home page with existing EDLs."""
    session = SessionLocal()
    edls = session.query(EDL).all()
    session.close()
    return render_template("index.html", edls=edls)

@edl_bp.route("/create", methods=["POST"])
@login_required
def create_edl():
    """Create a new External Dynamic List (EDL) with input validation and tracking the creator."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    # Validate name
    if len(name) < 4:
        flash("EDL name must be at least 4 characters long.", "error")
        return redirect(url_for("edl.home"))
    if not any(c.isalpha() for c in name):
        flash("EDL name must contain at least one alphabetical character.", "error")
        return redirect(url_for("edl.home"))
    if not re.match(r"^[a-zA-Z0-9]+$", name):
        flash("EDL name must be alphanumeric with no special characters or spaces.", "error")
        return redirect(url_for("edl.home"))

    # Validate description
    description, error = sanitize_description(description)
    if error:
        flash(error, "error")
        return redirect(url_for("edl.home"))

    session = SessionLocal()
    existing_edl = session.query(EDL).filter_by(name=name).first()
    if existing_edl:
        session.close()
        flash("EDL with this name already exists.", "error")
        return redirect(url_for("edl.home"))

    new_edl = EDL(name=name, description=description, created_by=current_user.username)  # Track creator
    session.add(new_edl)
    session.commit()
    session.close()

    flash("EDL created successfully!", "success")
    return redirect(url_for("edl.home"))

@edl_bp.route("/edl/<int:edl_id>")
def view_edl(edl_id):
    """View EDL details including its entries."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(id=edl_id).first()
    
    if not edl:
        session.close()
        return "EDL Not Found", 404

    entries = session.query(Entry).filter_by(edl_id=edl.id).all()
    session.close()

    return render_template("edl_details.html", edl=edl, entries=entries)

@edl_bp.route("/edl/<int:edl_id>/add_entry", methods=["POST"])
@login_required
def add_entry(edl_id):
    """Add an entry to an EDL with validation and track the creator."""
    value = request.form.get("value", "").strip()
    description = request.form.get("description", "").strip()

    # Validate value
    value, error = validate_entry_value(value)
    if error:
        flash(error, "error")
        return redirect(url_for("edl.view_edl", edl_id=edl_id))
    
    # Validate description
    description, error = sanitize_description(description)
    if error:
        flash(error, "error")
        return redirect(url_for("edl.view_edl", edl_id=edl_id))
    
    session = SessionLocal()
    new_entry = Entry(edl_id=edl_id, value=value, description=description, created_by=current_user.username)  # Track creator
    session.add(new_entry)
    session.commit()
    session.close()

    flash("Entry added successfully!", "success")
    return redirect(url_for("edl.view_edl", edl_id=edl_id))

@edl_bp.route("/entry/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    """Delete an entry from an EDL."""
    session = SessionLocal()
    entry = session.query(Entry).filter_by(id=entry_id).first()

    if not entry:
        session.close()
        return "Entry Not Found", 404

    session.delete(entry)
    session.commit()
    edl_id = entry.edl_id  # Get EDL ID before closing session
    session.close()

    return redirect(url_for("edl.view_edl", edl_id=edl_id))

@edl_bp.route("/edl/<int:edl_id>/delete", methods=["POST"])
@login_required
def delete_edl(edl_id):
    """Delete an entire EDL and its entries."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(id=edl_id).first()

    if not edl:
        session.close()
        return "EDL Not Found", 404

    session.delete(edl)  # Cascade deletion will remove associated entries
    session.commit()
    session.close()

    return redirect(url_for("edl.home"))

@edl_bp.route("/edl/<int:edl_id>/delete", methods=["GET"])
def delete_edl_confirmation(edl_id):
    """Show the delete confirmation page."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(id=edl_id).first()
    session.close()

    if not edl:
        return "EDL Not Found", 404

    return render_template("delete_edl.html", edl=edl)

@edl_bp.route("/edl/<int:edl_id>/confirm_delete", methods=["POST"])
@login_required
def confirm_delete_edl(edl_id):
    """Delete an EDL after confirmation."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(id=edl_id).first()

    if not edl:
        session.close()
        return "EDL Not Found", 404

    session.delete(edl)  # Cascade deletion removes associated entries
    session.commit()
    session.close()

    return redirect(url_for("edl.home"))

@edl_bp.route("/edl/<int:edl_id>/clone", methods=["GET"])
def clone_edl_form(edl_id):
    """Show the form to clone an EDL."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(id=edl_id).first()
    session.close()

    if not edl:
        return "EDL Not Found", 404

    return render_template("clone_edl.html", edl=edl)

@edl_bp.route("/edl/<int:edl_id>/confirm_clone", methods=["POST"])
@login_required
def clone_edl(edl_id):
    """Clone an EDL and its entries, then redirect to home."""
    new_name = request.form.get("new_name")
    description = request.form.get("description", f"Clone of {edl_id}")

    if not new_name:
        return redirect(url_for("edl.clone_edl_form", edl_id=edl_id))

    session = SessionLocal()
    original_edl = session.query(EDL).filter_by(id=edl_id).first()

    if not original_edl:
        session.close()
        return "EDL Not Found", 404

    # Create cloned EDL
    cloned_edl = EDL(name=new_name, description=description)
    session.add(cloned_edl)
    session.commit()

    # Copy entries
    for entry in original_edl.entries:
        cloned_entry = Entry(edl_id=cloned_edl.id, value=entry.value, description=entry.description)
        session.add(cloned_entry)

    session.commit()
    session.close()

    return redirect(url_for("edl.home"))  # Redirect to home instead of viewing the cloned EDL

@edl_bp.route("/edl/<string:edl_name>/entries.txt", methods=["GET"])
def get_edl_entries_plaintext(edl_name):
    """Return the EDL entries in plain text format based on the EDL name."""
    session = SessionLocal()
    edl = session.query(EDL).filter_by(name=edl_name).first()

    if not edl:
        session.close()
        return "EDL Not Found", 404

    entries = session.query(Entry).filter_by(edl_id=edl.id).all()
    session.close()

    response_text = "\n".join(
        f"{entry.value} #{entry.description} - Created at {entry.created_at}"
        for entry in entries
    )

    return response_text, 200, {"Content-Type": "text/plain"}


@edl_bp.route("/edl/<int:edl_id>/export/json")
@login_required
def export_edl_json(edl_id):
    """Export a single EDL and its entries as JSON."""
    session = SessionLocal()
    edl = session.query(EDL).options(joinedload(EDL.entries)).filter_by(id=edl_id).first()  # ✅ Preload entries
    session.close()

    if not edl:
        flash("EDL not found.", "error")
        return redirect(url_for("edl.home"))

    edl_data = {
        "id": edl.id,
        "name": edl.name,
        "description": edl.description,
        "created_by": edl.created_by,
        "created_at": edl.created_at.isoformat(),
        "entries": [
            {
                "id": entry.id,
                "value": entry.value,
                "description": entry.description,
                "created_by": entry.created_by,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in edl.entries  # ✅ Now this works!
        ]
    }

    return jsonify(edl_data)

@edl_bp.route("/edl/<int:edl_id>/export/csv")
@login_required
def export_edl_csv(edl_id):
    """Export a single EDL and its entries as CSV."""
    session = SessionLocal()
    edl = session.query(EDL).options(joinedload(EDL.entries)).filter_by(id=edl_id).first()
    
    if not edl:
        session.close()
        flash("EDL not found.", "error")
        return redirect(url_for("edl.home"))  # Ensure redirect if EDL is missing

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow(["EDL Name", "EDL Description", "Created By", "Entry ID", "Entry Value", "Entry Description", "Entry Created By", "Entry Created At"])

    # CSV Rows
    if edl.entries:
        for entry in edl.entries:
            writer.writerow([
                edl.name.replace(",", ""),  # Remove commas
                edl.description.replace(",", "") if edl.description else "",
                edl.created_by,
                entry.id,
                entry.value.replace(",", ""),  # Remove commas
                entry.description.replace(",", "") if entry.description else "",
                entry.created_by,
                entry.created_at
            ])

    session.close()  # Close the session properly

    response = Response(output.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={edl.name}_export.csv"
    return response  # Ensure response is always returned
