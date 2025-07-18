from flask import Flask, request, jsonify
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
users_db = [
    {
        "id": 1,
        "fullName": "Admin User",  # Fixed: Changed from "name" to "fullName"
        "email": "admin@turmadigital.com",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "position": "System Administrator",
        "department": "IT",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 2,
        "fullName": "John Doe",  # Fixed: Changed from "name" to "fullName"
        "email": "john.doe@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Software Developer",
        "department": "Engineering",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 3,
        "fullName": "Jane Smith",  # Fixed: Changed from "name" to "fullName"
        "email": "jane.smith@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "UI/UX Designer",
        "department": "Design",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 4,
        "fullName": "Mike Johnson",  # Fixed: Changed from "name" to "fullName"
        "email": "mike.johnson@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Project Manager",
        "department": "Operations",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    }
]

time_records_db = []
eod_reports_db = []
announcements_db = [
    {
        "id": 1,
        "title": "Welcome to Turma Digital Agency",
        "content": "Welcome to our new employee management system. Please familiarize yourself with all the features.",
        "priority": "normal",
        "date": "2024-01-15",
        "created_by": 1,
        "created_at": "2024-01-15T09:00:00"
    },
    {
        "id": 2,
        "title": "System Maintenance",
        "content": "Scheduled maintenance will occur this weekend. Please save your work regularly.",
        "priority": "high",
        "date": "2024-01-16",
        "created_by": 1,
        "created_at": "2024-01-16T10:00:00"
    }
]

# Request management databases
leave_requests_db = []
salary_loan_requests_db = []
time_adjustment_requests_db = []

# Training materials database - will be loaded from Excel file
training_materials_db = []

# Active sessions for real-time sync - Fixed: Enhanced tracking
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_id(user_id):
    return next((user for user in users_db if user['id'] == user_id and user.get('is_active', True)), None)

def get_user_by_email(email):
    return next((user for user in users_db if user['email'] == email and user.get('is_active', True)), None)

def generate_password():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def update_user_activity(user_id):
    """Update user's last activity and ensure they're in active sessions"""
    if user_id not in active_sessions:
        user = get_user_by_id(user_id)
        if user:
            active_sessions[user_id] = {
                "user_id": user_id,
                "user_name": user['fullName'],
                "login_time": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "status": "online"
            }
    else:
        active_sessions[user_id]["last_activity"] = datetime.now().isoformat()
        active_sessions[user_id]["status"] = "online"

def get_user_clock_status(user_id):
    """Get current clock-in status for a user"""
    today = datetime.now().strftime('%Y-%m-%d')
    record = next((record for record in time_records_db 
                  if record['employee_id'] == user_id and record['date'] == today), None)
    
    if not record:
        return "not_clocked_in"
    elif record.get('clock_out'):
        return "clocked_out"
    else:
        return "clocked_in"

# Root endpoint
@app.route('/')
def hello():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
        "version": "2.1.0",
        "training_materials_count": len(training_materials_db)
    })

# API health check
@app.route('/api')
def api_root():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
        "training_materials_loaded": len(training_materials_db),
        "endpoints": [
            "/api/auth/login",
            "/api/auth/verify",
            "/api/admin/employees",
            "/api/admin/time-records",
            "/api/admin/eod-reports",
            "/api/employee/clock-in",
            "/api/employee/clock-out",
            "/api/employee/eod-report",
            "/api/announcements",
            "/api/training/materials",
            "/api/requests/leave",
            "/api/requests/salary-loan",
            "/api/requests/time-adjustment",
            "/api/admin/users/create",
            "/api/admin/users/update",
            "/api/admin/users/regenerate-password",
            "/api/admin/users/delete",
            "/api/admin/export/time-records",
            "/api/admin/export/eod-reports",
            "/api/system/health",
            "/api/realtime/status"
        ]
    })

# System health endpoint
@app.route('/api/system/health')
def system_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "api": "operational",
        "active_sessions": len(active_sessions),
        "training_materials_loaded": len(training_materials_db)
    })

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400
    
    user = get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != hashed_password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    token = generate_token(user['id'])
    user_data = {k: v for k, v in user.items() if k != 'password'}
    
    # Track active session with enhanced info
    active_sessions[user['id']] = {
        "user_id": user['id'],
        "user_name": user['fullName'],
        "login_time": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "status": get_user_clock_status(user['id'])
    }
    
    return jsonify({
        "success": True,
        "token": token,
        "user": user_data
    })

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Update activity and status
    update_user_activity(user_id)
    active_sessions[user_id]["status"] = get_user_clock_status(user_id)
    
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({"success": True, "user": user_data})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if user_id and user_id in active_sessions:
        del active_sessions[user_id]
    
    return jsonify({"success": True, "message": "Logged out successfully"})

# Admin endpoints
@app.route('/api/admin/employees', methods=['GET'])
def get_employees():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    employees = [{k: v for k, v in emp.items() if k != 'password'} for emp in users_db if emp.get('is_active', True)]
    
    # Add enhanced active session info
    for emp in employees:
        emp['is_online'] = emp['id'] in active_sessions
        if emp['is_online']:
            session_info = active_sessions[emp['id']]
            emp['last_activity'] = session_info['last_activity']
            emp['clock_status'] = session_info.get('status', get_user_clock_status(emp['id']))
            emp['login_time'] = session_info.get('login_time')
        else:
            emp['clock_status'] = get_user_clock_status(emp['id'])
    
    return jsonify({"success": True, "employees": employees})

@app.route('/api/admin/time-records', methods=['GET'])
def get_time_records():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Enrich time records with employee names
    enriched_records = []
    for record in time_records_db:
        employee = get_user_by_id(record['employee_id'])
        if employee:
            enriched_record = record.copy()
            enriched_record['employee_name'] = employee['fullName']
            enriched_record['employee_email'] = employee['email']
            enriched_records.append(enriched_record)
    
    return jsonify({"success": True, "records": enriched_records})

@app.route('/api/admin/eod-reports', methods=['GET'])
def get_eod_reports():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Enrich EOD reports with employee names
    enriched_reports = []
    for report in eod_reports_db:
        employee = get_user_by_id(report['employee_id'])
        if employee:
            enriched_report = report.copy()
            enriched_report['employee_name'] = employee['fullName']
            enriched_report['employee_email'] = employee['email']
            enriched_reports.append(enriched_report)
    
    return jsonify({"success": True, "reports": enriched_reports})

# User Management Endpoints
@app.route('/api/admin/users/create', methods=['POST'])
def create_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    # Check if email already exists
    if get_user_by_email(data.get('email')):
        return jsonify({"success": False, "message": "Email already exists"}), 400
    
    # Generate password if not provided
    password = data.get('password', generate_password())
    
    new_user = {
        "id": max([u['id'] for u in users_db]) + 1,
        "fullName": data.get('fullName') or data.get('name'),  # Support both field names
        "email": data.get('email'),
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "role": data.get('role', 'employee'),
        "position": data.get('position', ''),
        "department": data.get('department', ''),
        "created_at": datetime.now().isoformat(),
        "is_active": True
    }
    
    users_db.append(new_user)
    
    # Return user data without password but include generated password for admin
    user_data = {k: v for k, v in new_user.items() if k != 'password'}
    user_data['generated_password'] = password
    
    return jsonify({"success": True, "user": user_data})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    admin_user_id = verify_token(token)
    
    if not admin_user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    admin_user = get_user_by_id(admin_user_id)
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    data = request.get_json()
    
    # Update user fields
    if 'fullName' in data or 'name' in data:
        target_user['fullName'] = data.get('fullName') or data.get('name')
    if 'email' in data:
        # Check if new email already exists
        existing_user = get_user_by_email(data['email'])
        if existing_user and existing_user['id'] != user_id:
            return jsonify({"success": False, "message": "Email already exists"}), 400
        target_user['email'] = data['email']
    if 'position' in data:
        target_user['position'] = data['position']
    if 'department' in data:
        target_user['department'] = data['department']
    if 'role' in data:
        target_user['role'] = data['role']
    if 'is_active' in data:
        target_user['is_active'] = data['is_active']
    
    user_data = {k: v for k, v in target_user.items() if k != 'password'}
    return jsonify({"success": True, "user": user_data})

@app.route('/api/admin/users/<int:user_id>/regenerate-password', methods=['POST'])
def regenerate_password(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    admin_user_id = verify_token(token)
    
    if not admin_user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    admin_user = get_user_by_id(admin_user_id)
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    new_password = generate_password()
    target_user['password'] = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Remove user from active sessions to force re-login
    if user_id in active_sessions:
        del active_sessions[user_id]
    
    return jsonify({"success": True, "new_password": new_password})

@app.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
def delete_user(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    admin_user_id = verify_token(token)
    
    if not admin_user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    admin_user = get_user_by_id(admin_user_id)
    if not admin_user or admin_user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    # Prevent admin from deleting themselves
    if user_id == admin_user_id:
        return jsonify({"success": False, "message": "Cannot delete your own account"}), 400
    
    target_user = get_user_by_id(user_id)
    if not target_user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Soft delete - mark as inactive instead of removing from database
    target_user['is_active'] = False
    target_user['deleted_at'] = datetime.now().isoformat()
    target_user['deleted_by'] = admin_user_id
    
    # Remove user from active sessions
    if user_id in active_sessions:
        del active_sessions[user_id]
    
    # Clean up user's data (optional - you might want to keep for audit purposes)
    # Remove time records, EOD reports, and requests for this user
    global time_records_db, eod_reports_db, leave_requests_db, salary_loan_requests_db, time_adjustment_requests_db
    
    # Mark user's records as deleted but keep for audit trail
    for record in time_records_db:
        if record['employee_id'] == user_id:
            record['user_deleted'] = True
    
    for report in eod_reports_db:
        if report['employee_id'] == user_id:
            report['user_deleted'] = True
    
    for request in leave_requests_db:
        if request['employee_id'] == user_id:
            request['user_deleted'] = True
    
    for request in salary_loan_requests_db:
        if request['employee_id'] == user_id:
            request['user_deleted'] = True
    
    for request in time_adjustment_requests_db:
        if request['employee_id'] == user_id:
            request['user_deleted'] = True
    
    user_data = {k: v for k, v in target_user.items() if k != 'password'}
    return jsonify({"success": True, "message": "User deleted successfully", "user": user_data})

# Employee endpoints
@app.route('/api/employee/clock-in', methods=['POST'])
def clock_in():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    # Check if already clocked in today
    today = datetime.now().strftime('%Y-%m-%d')
    existing_record = next((record for record in time_records_db 
                          if record['employee_id'] == user_id and record['date'] == today), None)
    
    if existing_record and not existing_record.get('clock_out'):
        return jsonify({"success": False, "message": "Already clocked in today"}), 400
    
    time_record = {
        "id": len(time_records_db) + 1,
        "employee_id": user_id,
        "date": today,
        "clock_in": datetime.now().isoformat(),
        "clock_out": None
    }
    
    time_records_db.append(time_record)
    
    # Update active session status
    update_user_activity(user_id)
    active_sessions[user_id]["status"] = "clocked_in"
    
    return jsonify({"success": True, "message": "Clocked in successfully", "record": time_record})

@app.route('/api/employee/clock-out', methods=['POST'])
def clock_out():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    today = datetime.now().strftime('%Y-%m-%d')
    record = next((record for record in time_records_db 
                  if record['employee_id'] == user_id and record['date'] == today), None)
    
    if not record:
        return jsonify({"success": False, "message": "No clock-in record found for today"}), 400
    
    if record.get('clock_out'):
        return jsonify({"success": False, "message": "Already clocked out today"}), 400
    
    record['clock_out'] = datetime.now().isoformat()
    
    # Update active session status
    update_user_activity(user_id)
    active_sessions[user_id]["status"] = "clocked_out"
    
    return jsonify({"success": True, "message": "Clocked out successfully", "record": record})

@app.route('/api/employee/eod-report', methods=['POST'])
def submit_eod_report():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    data = request.get_json()
    
    eod_report = {
        "id": len(eod_reports_db) + 1,
        "employee_id": user_id,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "tasks_completed": data.get('tasks_completed', ''),
        "challenges": data.get('challenges', ''),
        "tomorrow_plan": data.get('tomorrow_plan', ''),
        "submitted_at": datetime.now().isoformat()
    }
    
    eod_reports_db.append(eod_report)
    return jsonify({"success": True, "message": "EOD report submitted successfully", "report": eod_report})

# Announcements endpoints
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    # Sort announcements by date (newest first)
    sorted_announcements = sorted(announcements_db, key=lambda x: x['created_at'], reverse=True)
    return jsonify({"success": True, "announcements": sorted_announcements})

@app.route('/api/announcements', methods=['POST'])
def create_announcement():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user['role'] != 'admin':
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    announcement = {
        "id": len(announcements_db) + 1,
        "title": data.get('title'),
        "content": data.get('content'),
        "priority": data.get('priority', 'normal'),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "created_by": user_id,
        "created_at": datetime.now().isoformat()
    }
    
    announcements_db.append(announcement)
    return jsonify({"success": True, "announcement": announcement})

# Request Management Endpoints (Leave, Salary Loan, Time Adjustment)
# [Previous request management code remains the same...]

# Training materials endpoints - FIXED
@app.route('/api/training/materials', methods=['GET'])
def get_training_materials():
    return jsonify({"success": True, "materials": training_materials_db, "count": len(training_materials_db)})



# Real-time status endpoint - FIXED
@app.route('/api/realtime/status', methods=['GET'])
def get_realtime_status():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    # Update last activity
    update_user_activity(user_id)
    
    # Clean up stale sessions (older than 5 minutes)
    current_time = datetime.now()
    stale_sessions = []
    for session_id, session_data in active_sessions.items():
        last_activity = datetime.fromisoformat(session_data['last_activity'])
        if (current_time - last_activity).total_seconds() > 300:  # 5 minutes
            stale_sessions.append(session_id)
    
    for session_id in stale_sessions:
        del active_sessions[session_id]
    
    status_data = {
        "active_users": len(active_sessions),
        "pending_leave_requests": len([req for req in leave_requests_db if req['status'] == 'pending']),
        "pending_loan_requests": len([req for req in salary_loan_requests_db if req['status'] == 'pending']),
        "pending_time_adjustments": len([req for req in time_adjustment_requests_db if req['status'] == 'pending']),
        "recent_announcements": len([ann for ann in announcements_db if ann['date'] == datetime.now().strftime('%Y-%m-%d')]),
        "timestamp": datetime.now().isoformat(),
        "training_materials_count": len(training_materials_db)
    }
    
    if user['role'] == 'admin':
        # Enhanced session info for admin
        status_data['active_sessions'] = []
        for session_id, session_data in active_sessions.items():
            session_user = get_user_by_id(session_id)
            if session_user:
                enhanced_session = session_data.copy()
                enhanced_session['clock_status'] = get_user_clock_status(session_id)
                status_data['active_sessions'].append(enhanced_session)
    
    return jsonify({"success": True, "status": status_data})

# CSV Export endpoints remain the same...




@app.route("/api/training/materials", methods=["POST"])
def create_training_material():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"success": False, "message": "No token provided"}), 401
    
    token = auth_header.split(" ")[1]
    user_id = verify_token(token)
    
    if not user_id:
        return jsonify({"success": False, "message": "Invalid token"}), 401
    
    user = get_user_by_id(user_id)
    if not user or user["role"] != "admin":
        return jsonify({"success": False, "message": "Admin access required"}), 403
    
    data = request.get_json()
    
    new_material = {
        "id": len(training_materials_db) + 1,
        "Tutorial Title": data.get("Tutorial Title"),
        "Article Link": data.get("Article Link"),
        "Video": data.get("Video"),
        "Categories": data.get("Categories"),
        "Tags": data.get("Tags"),
        "Application": data.get("Application"),
        "Description": data.get("Description"),
        "Difficulty": data.get("Difficulty"),
        "created_at": datetime.now().isoformat()
    }
    
    training_materials_db.append(new_material)
    return jsonify({"success": True, "material": new_material})


