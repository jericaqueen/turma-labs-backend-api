from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import hashlib
import json
import csv
import io
import os

app = Flask(__name__)
CORS(app, origins="*")

# Secret key for JWT
SECRET_KEY = "turma-digital-agency-secret-key-2024"

# In-memory database (replace with real database in production)
users_db = {
    "admin@turmadigital.com": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin"},
    "employee@turmadigital.com": {"password": hashlib.sha256("employee123".encode()).hexdigest(), "role": "employee"}
}

training_materials_db = [
    {"id": 1, "title": "Onboarding Guide", "content": "Welcome to Turma Digital Agency! This guide will help you get started.", "category": "General"},
    {"id": 2, "title": "Social Media Marketing Best Practices", "content": "Learn the best strategies for effective social media campaigns.", "category": "Marketing"},
    {"id": 3, "title": "SEO Fundamentals", "content": "Understand the basics of Search Engine Optimization.", "category": "SEO"}
]

time_logs_db = []

# Helper function to generate JWT token
def generate_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Helper function to decode JWT token
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}

# Middleware to protect routes
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = decode_token(token)
            if "error" in data:
                return jsonify({"message": data["error"]}), 401
            current_user = data["user_id"]
            current_user_role = data["role"]
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, current_user_role, *args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated

# Admin role required decorator
def admin_required(f):
    def decorated_function(current_user, current_user_role, *args, **kwargs):
        if current_user_role != "admin":
            return jsonify({"message": "Admin access required!"}), 403
        return f(current_user, current_user_role, *args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Health check route
@app.route("/", methods=["GET"])
@app.route("/api", methods=["GET"])
def health_check():
    return jsonify({"message": "Turma Labs Backend API is running", "status": "healthy"})

# Routes
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        user = users_db.get(email)

        if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({"message": "Invalid credentials"}), 401

        token = generate_token(email, user["role"])
        return jsonify({"token": token, "role": user["role"]})
    except Exception as e:
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

@app.route("/api/dashboard", methods=["GET"])
@token_required
def dashboard(current_user, current_user_role):
    return jsonify({"message": f"Welcome to the dashboard, {current_user}! Your role is {current_user_role}."})

@app.route("/api/training_materials", methods=["GET"])
@token_required
def get_training_materials(current_user, current_user_role):
    return jsonify(training_materials_db)

@app.route("/api/training_materials", methods=["POST"])
@token_required
@admin_required
def add_training_material(current_user, current_user_role):
    try:
        data = request.get_json()
        new_id = max([m["id"] for m in training_materials_db]) + 1 if training_materials_db else 1
        new_material = {"id": new_id, "title": data["title"], "content": data["content"], "category": data["category"]}
        training_materials_db.append(new_material)
        return jsonify(new_material), 201
    except Exception as e:
        return jsonify({"message": "Error adding training material", "error": str(e)}), 500

@app.route("/api/training_materials/<int:material_id>", methods=["PUT"])
@token_required
@admin_required
def update_training_material(current_user, current_user_role, material_id):
    try:
        data = request.get_json()
        material = next((m for m in training_materials_db if m["id"] == material_id), None)
        if material:
            material.update(data)
            return jsonify(material)
        return jsonify({"message": "Material not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error updating training material", "error": str(e)}), 500

@app.route("/api/training_materials/<int:material_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_training_material(current_user, current_user_role, material_id):
    try:
        global training_materials_db
        initial_len = len(training_materials_db)
        training_materials_db = [m for m in training_materials_db if m["id"] != material_id]
        if len(training_materials_db) < initial_len:
            return jsonify({"message": "Material deleted"}), 204
        return jsonify({"message": "Material not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error deleting training material", "error": str(e)}), 500

@app.route("/api/time_logs", methods=["POST"])
@token_required
def clock_in_out(current_user, current_user_role):
    try:
        data = request.get_json()
        log_type = data.get("type")  # "clock_in" or "clock_out"

        if log_type == "clock_in":
            new_log = {"user": current_user, "type": "clock_in", "timestamp": datetime.now().isoformat()}
            time_logs_db.append(new_log)
            return jsonify({"message": "Clocked in successfully", "log": new_log}), 201
        elif log_type == "clock_out":
            new_log = {"user": current_user, "type": "clock_out", "timestamp": datetime.now().isoformat()}
            time_logs_db.append(new_log)
            return jsonify({"message": "Clocked out successfully", "log": new_log}), 201
        return jsonify({"message": "Invalid log type"}), 400
    except Exception as e:
        return jsonify({"message": "Error processing time log", "error": str(e)}), 500

@app.route("/api/time_logs", methods=["GET"])
@token_required
def get_time_logs(current_user, current_user_role):
    try:
        if current_user_role == "admin":
            return jsonify(time_logs_db)
        else:
            user_logs = [log for log in time_logs_db if log["user"] == current_user]
            return jsonify(user_logs)
    except Exception as e:
        return jsonify({"message": "Error retrieving time logs", "error": str(e)}), 500

@app.route("/api/users", methods=["GET"])
@token_required
@admin_required
def get_users(current_user, current_user_role):
    try:
        # Return user emails and roles, excluding passwords
        users_info = [{
            "email": email,
            "role": users_db[email]["role"]
        } for email in users_db]
        return jsonify(users_info)
    except Exception as e:
        return jsonify({"message": "Error retrieving users", "error": str(e)}), 500

@app.route("/api/export_data", methods=["GET"])
@token_required
@admin_required
def export_data(current_user, current_user_role):
    try:
        data_type = request.args.get("type")

        if data_type == "users":
            si = io.StringIO()
            cw = csv.writer(si)
            cw.writerow(["Email", "Role"])
            for email, user_data in users_db.items():
                cw.writerow([email, user_data["role"]])
            output = si.getvalue()
            return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=users.csv"})
        elif data_type == "training_materials":
            si = io.StringIO()
            cw = csv.writer(si)
            cw.writerow(["ID", "Title", "Content", "Category"])
            for material in training_materials_db:
                cw.writerow([material["id"], material["title"], material["content"], material["category"]])
            output = si.getvalue()
            return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=training_materials.csv"})
        elif data_type == "time_logs":
            si = io.StringIO()
            cw = csv.writer(si)
            cw.writerow(["User", "Type", "Timestamp"])
            for log in time_logs_db:
                cw.writerow([log["user"], log["type"], log["timestamp"]])
            output = si.getvalue()
            return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=time_logs.csv"})

        return jsonify({"message": "Invalid data type for export"}), 400
    except Exception as e:
        return jsonify({"message": "Error exporting data", "error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
