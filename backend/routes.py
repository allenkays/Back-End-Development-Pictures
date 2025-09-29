from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################

@app.route("/picture", methods=["GET"])
def get_pictures():
    return jsonify(data), 200


######################################################################
# GET A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    """Return a picture by its ID"""
    picture = next((item for item in data if item["id"] == id), None)
    if picture:
        return jsonify(picture), 200
    return {"message": f"Picture with id {id} not found"}, 404


######################################################################
# CREATE A PICTURE
######################################################################

@app.route("/picture", methods=["POST"])
def create_picture():
    """Create a new picture"""
    picture = request.get_json()
    if not picture or "id" not in picture:
        return {"message": "Invalid input, 'id' is required"}, 400

    # Check if ID already exists
    if any(item["id"] == picture["id"] for item in data):
        return {"message": f"picture with id {picture['id']} already present"}, 422

    # Append new picture to data
    data.append(picture)
    
    # Save updated data to JSON file
    try:
        with open(json_url, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify(picture), 201
    except Exception:
        return {"message": "Internal server error"}, 500


######################################################################
# UPDATE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    """Update a picture by its ID"""
    picture = next((item for item in data if item["id"] == id), None)
    if not picture:
        return {"message": f"Picture with id {id} not found"}, 404

    updated_picture = request.get_json()
    if not updated_picture:
        return {"message": "Invalid input"}, 400

    # Update the picture (preserve the ID)
    updated_picture["id"] = id
    picture.update(updated_picture)
    
    # Save updated data to JSON file
    try:
        with open(json_url, "w") as f:
            json.dump(data, f, indent=2)
        return jsonify(picture), 200
    except Exception:
        return {"message": "Internal server error"}, 500


######################################################################
# DELETE A PICTURE
######################################################################

@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    """Delete a picture by its ID"""
    global data
    picture = next((item for item in data if item["id"] == id), None)
    if not picture:
        return {"message": f"Picture with id {id} not found"}, 404

    # Remove the picture from data
    data = [item for item in data if item["id"] != id]
    
    # Save updated data to JSON file
    try:
        with open(json_url, "w") as f:
            json.dump(data, f, indent=2)
        return {}, 204  # 204 typically has no body
    except Exception:
        return {"message": "Internal server error"}, 500
