from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import hashlib
import json

app = Flask(__name__)
CORS(app, origins="*")

# Secret key for JWT
SECRET_KEY = "turma-digital-agency-secret-key-2024"

# In-memory database (replace with real database in production)
users_db = [
    {
        "id": 1,
        "name": "Admin User",
        "email": "admin@turmadigital.com",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "position": "System Administrator",
        "department": "IT"
    },
    {
        "id": 2,
        "name": "John Doe",
        "email": "john.doe@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Software Developer",
        "department": "Engineering"
    },
    {
        "id": 3,
        "name": "Jane Smith",
        "email": "jane.smith@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "UI/UX Designer",
        "department": "Design"
    },
    {
        "id": 4,
        "name": "Mike Johnson",
        "email": "mike.johnson@turmadigital.com",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "employee",
        "position": "Project Manager",
        "department": "Operations"
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
        "created_by": 1
    },
    {
        "id": 2,
        "title": "System Maintenance",
        "content": "Scheduled maintenance will occur this weekend. Please save your work regularly.",
        "priority": "high",
        "date": "2024-01-16",
        "created_by": 1
    }
]

training_materials_db = [
    {
        "id": 1,
        "title": "Company Onboarding",
        "description": "Complete guide to company policies and procedures",
        "duration": "2 hours",
        "required": True,
        "category": "Onboarding"
    },
    {
        "id": 2,
        "title": "Security Training",
        "description": "Learn about cybersecurity best practices",
        "duration": "1 hour",
        "required": True,
        "category": "Security"
    },
    {
        "id": 3,
        "title": "Professional Development",
        "description": "Skills development and career growth",
        "duration": "3 hours",
        "required": False,
        "category": "Development"
    }
]

def generate_token(user_id):
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
    return next((user for user in users_db if user['id'] == user_id), None)

def get_user_by_email(email):
    return next((user for user in users_db if user['email'] == email), None)

# Root endpoint
@app.route('/')
def hello():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
        "version": "1.0.0"
    })

# API health check
@app.route('/api')
def api_root():
    return jsonify({
        "message": "Turma Digital Agency Backend API",
        "status": "running",
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
            "/api/system/health"
        ]
    })

# System health endpoint
@app.route('/api/system/health')
def system_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "api": "operational"
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
    
    user_data = {k: v for k, v in user.items() if k != 'password'}
    return jsonify({"success": True, "user": user_data})

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
    
    employees = [{k: v for k, v in emp.items() if k != 'password'} for emp in users_db]
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
    
    return jsonify({"success": True, "records": time_records_db})

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
    
    return jsonify({"success": True, "reports": eod_reports_db})

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
    return jsonify({"success": True, "message": "Clocked in successfully"})

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
    return jsonify({"success": True, "message": "Clocked out successfully"})

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
    return jsonify({"success": True, "message": "EOD report submitted successfully"})

# Announcements endpoints
@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    return jsonify({"success": True, "announcements": announcements_db})

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
        "created_by": user_id
    }
    
    announcements_db.append(announcement)
    return jsonify({"success": True, "announcement": announcement})

# Training materials endpoints
@app.route('/api/training/materials', methods=['GET'])
def get_training_materials():
    return jsonify({"success": True, "materials": training_materials_db})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
