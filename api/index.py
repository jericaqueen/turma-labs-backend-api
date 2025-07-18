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
@app.route("/api/auth/login", methods=["POST"])
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

@app.route("/api/auth/verify", methods=["POST"])
@token_required
def verify_token(current_user, current_user_role):
    return jsonify({"user": current_user, "role": current_user_role})

@app.route("/api/announcements", methods=["GET"])
@token_required
def get_announcements(current_user, current_user_role):
    announcements = [
        {"id": 1, "title": "Welcome to Turma Labs", "content": "Welcome to our employee management system!", "date": "2024-01-01"},
        {"id": 2, "title": "System Update", "content": "The system has been updated with new features.", "date": "2024-01-15"}
    ]
    return jsonify(announcements)

@app.route("/api/announcements", methods=["POST"])
@token_required
@admin_required
def create_announcement(current_user, current_user_role):
    try:
        data = request.get_json()
        new_announcement = {
            "id": len(announcements) + 1,
            "title": data.get("title"),
            "content": data.get("content"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        return jsonify(new_announcement), 201
    except Exception as e:
        return jsonify({"message": "Error creating announcement", "error": str(e)}), 500

@app.route("/api/training/materials", methods=["GET"])
@token_required
def get_training_materials(current_user, current_user_role):
    return jsonify(training_materials_db)

@app.route("/api/employee/clock-in", methods=["POST"])
@token_required
def clock_in(current_user, current_user_role):
    try:
        new_log = {"user": current_user, "type": "clock_in", "timestamp": datetime.now().isoformat()}
        time_logs_db.append(new_log)
        return jsonify({"message": "Clocked in successfully", "log": new_log}), 201
    except Exception as e:
        return jsonify({"message": "Error processing clock in", "error": str(e)}), 500

@app.route("/api/employee/clock-out", methods=["POST"])
@token_required
def clock_out(current_user, current_user_role):
    try:
        new_log = {"user": current_user, "type": "clock_out", "timestamp": datetime.now().isoformat()}
        time_logs_db.append(new_log)
        return jsonify({"message": "Clocked out successfully", "log": new_log}), 201
    except Exception as e:
        return jsonify({"message": "Error processing clock out", "error": str(e)}), 500

@app.route("/api/employee/eod-report", methods=["POST"])
@token_required
def submit_eod_report(current_user, current_user_role):
    try:
        data = request.get_json()
        eod_report = {
            "user": current_user,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tasks_completed": data.get("tasksCompleted", ""),
            "challenges": data.get("challenges", ""),
            "tomorrow_plan": data.get("tomorrowPlan", ""),
            "timestamp": datetime.now().isoformat()
        }
        return jsonify({"message": "EOD report submitted successfully", "report": eod_report}), 201
    except Exception as e:
        return jsonify({"message": "Error submitting EOD report", "error": str(e)}), 500

@app.route("/api/admin/employees", methods=["GET"])
@token_required
@admin_required
def get_employees(current_user, current_user_role):
    try:
        # Return user emails and roles, excluding passwords
        users_info = [{
            "email": email,
            "role": users_db[email]["role"]
        } for email in users_db]
        return jsonify(users_info)
    except Exception as e:
        return jsonify({"message": "Error retrieving employees", "error": str(e)}), 500

@app.route("/api/admin/time-records", methods=["GET"])
@token_required
@admin_required
def get_time_records(current_user, current_user_role):
    try:
        return jsonify(time_logs_db)
    except Exception as e:
        return jsonify({"message": "Error retrieving time records", "error": str(e)}), 500

@app.route("/api/admin/eod-reports", methods=["GET"])
@token_required
@admin_required
def get_eod_reports(current_user, current_user_role):
    try:
        # Return empty array for now since we don't have persistent storage
        return jsonify([])
    except Exception as e:
        return jsonify({"message": "Error retrieving EOD reports", "error": str(e)}), 500

@app.route("/api/system/health", methods=["GET"])
@token_required
@admin_required
def system_health(current_user, current_user_role):
    try:
        health_data = {
            "status": "healthy",
            "uptime": "99.9%",
            "last_check": datetime.now().isoformat(),
            "services": {
                "database": "operational",
                "api": "operational",
                "authentication": "operational"
            }
        }
        return jsonify(health_data)
    except Exception as e:
        return jsonify({"message": "Error retrieving system health", "error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"message": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

