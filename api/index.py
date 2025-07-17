from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def hello():
    return {"message": "Turma Labs Backend API", "status": "running"}

@app.route('/api')
def api_root():
    return {"message": "Turma Labs Backend API", "status": "running"}

@app.route('/api/health')
def health_check():
    return {"status": "healthy", "service": "Turma Labs Backend API"}

@app.route('/api/employees')
def get_employees():
    # Sample employee data
    employees = [
        {"id": 1, "name": "John Doe", "position": "Developer", "department": "IT"},
        {"id": 2, "name": "Jane Smith", "position": "Designer", "department": "Design"},
        {"id": 3, "name": "Mike Johnson", "position": "Manager", "department": "Operations"}
    ]
    return {"employees": employees, "count": len(employees)}

# This is the entry point for Vercel
def handler(request, response):
    return app(request, response)

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
