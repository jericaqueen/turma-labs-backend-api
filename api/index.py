from flask import Flask, request
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

# Vercel serverless function handler
def handler(event, context):
    return app

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
