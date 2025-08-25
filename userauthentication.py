from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import re
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a secure secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Input validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

def validate_username(username):
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Database helper functions
def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

# HTML Templates (embedded for simplicity)
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Authentication App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { margin: 0 10px; color: #007bff; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Welcome to Authentication App</h2>
        <p>Please register or login to continue.</p>
        <div class="nav">
            <a href="/register">Register</a> |
            <a href="/login">Login</a> |
            <a href="/api/status">Check Status</a>
        </div>
    </div>
</body>
</html>
'''

REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Register - Authentication App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { margin: 0 10px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Register</h2>
        <form method="POST">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        <div class="nav">
            <a href="/login">Already have an account? Login</a> |
            <a href="/">Home</a>
        </div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Authentication App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
        .success { color: green; margin-top: 10px; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { margin: 0 10px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login</h2>
        <form method="POST">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="nav">
            <a href="/register">Don't have an account? Register</a> |
            <a href="/">Home</a>
        </div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        {% if success %}
        <div class="success">{{ success }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Authentication App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .user-info { background: #e9ecef; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .logout-btn { background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .logout-btn:hover { background: #c82333; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { margin: 0 10px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Dashboard</h2>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="user-info">
            <h3>Welcome, {{ username }}!</h3>
            <p><strong>Email:</strong> {{ email }}</p>
            <p><strong>User ID:</strong> {{ user_id }}</p>
            <p><strong>Member Since:</strong> {{ created_at }}</p>
        </div>
        
        <h3>Protected Content</h3>
        <p>🎉 Congratulations! You have successfully logged in and can now access protected routes.</p>
        <p>This dashboard is only accessible to authenticated users.</p>
        
        <div class="nav">
            <a href="/profile">View Profile</a> |
            <a href="/api/status">Check Status</a>
        </div>
    </div>
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Profile - Authentication App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .profile-info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .profile-info h3 { margin-top: 0; color: #495057; }
        .profile-item { margin-bottom: 15px; padding: 10px; background: white; border-left: 4px solid #007bff; }
        .logout-btn { background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .logout-btn:hover { background: #c82333; }
        .nav { text-align: center; margin-top: 20px; }
        .nav a { margin: 0 10px; color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>User Profile</h2>
            <a href="/logout" class="logout-btn">Logout</a>
        </div>
        
        <div class="profile-info">
            <h3>Profile Information</h3>
            
            <div class="profile-item">
                <strong>Username:</strong> {{ username }}
            </div>
            
            <div class="profile-item">
                <strong>Email Address:</strong> {{ email }}
            </div>
            
            <div class="profile-item">
                <strong>User ID:</strong> {{ user_id }}
            </div>
            
            <div class="profile-item">
                <strong>Account Created:</strong> {{ created_at }}
            </div>
        </div>
        
        <p><em>This is another protected route that requires authentication to access.</em></p>
        
        <div class="nav">
            <a href="/dashboard">Back to Dashboard</a> |
            <a href="/api/status">Check Status</a>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate inputs
        if not username or not email or not password:
            return render_template_string(REGISTER_TEMPLATE, error="All fields are required")
        
        # Validate username
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            return render_template_string(REGISTER_TEMPLATE, error=username_msg)
        
        # Validate email
        if not validate_email(email):
            return render_template_string(REGISTER_TEMPLATE, error="Invalid email format")
        
        # Validate password
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            return render_template_string(REGISTER_TEMPLATE, error=password_msg)
        
        # Check if user already exists
        if get_user_by_email(email):
            return render_template_string(REGISTER_TEMPLATE, error="Email already registered")
        
        if get_user_by_username(username):
            return render_template_string(REGISTER_TEMPLATE, error="Username already taken")
        
        # Create user
        user_id = create_user(username, email, password)
        if user_id:
            return render_template_string(REGISTER_TEMPLATE, success="Registration successful! You can now login.")
        else:
            return render_template_string(REGISTER_TEMPLATE, error="Registration failed. Please try again.")
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            return render_template_string(LOGIN_TEMPLATE, error="Email and password are required")
        
        # Get user from database
        user = get_user_by_email(email)
        if user and check_password_hash(user[3], password):  # user[3] is password_hash
            session.permanent = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid email or password")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    username=user[1], 
                                    email=user[2], 
                                    user_id=user[0],
                                    created_at=user[4])
    else:
        session.clear()
        return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return render_template_string(PROFILE_TEMPLATE, 
                                    username=user[1], 
                                    email=user[2], 
                                    user_id=user[0],
                                    created_at=user[4])
    else:
        session.clear()
        return redirect(url_for('login'))

# API Routes
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate inputs
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Validate username
    username_valid, username_msg = validate_username(username)
    if not username_valid:
        return jsonify({'error': username_msg}), 400
    
    # Validate email
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return jsonify({'error': password_msg}), 400
    
    # Check if user already exists
    if get_user_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409
    
    if get_user_by_username(username):
        return jsonify({'error': 'Username already taken'}), 409
    
    # Create user
    user_id = create_user(username, email, password)
    if user_id:
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'username': username,
            'email': email
        }), 201
    else:
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user from database
    user = get_user_by_email(email)
    if user and check_password_hash(user[3], password):
        session.permanent = True
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['email'] = user[2]
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'email': session['email']
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 200

@app.route('/api/profile', methods=['GET'])
@login_required
def api_profile():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'created_at': user[4]
            }
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404

if __name__ == '__main__':
    init_db()
    print("🚀 Authentication App Starting...")
    print("📝 Demo Credentials:")
    print("   Username: testuser")
    print("   Email: test@example.com")
    print("   Password: TestPass123")
    
    # Create demo user if it doesn't exist
    if not get_user_by_email('test@example.com'):
        create_user('testuser', 'test@example.com', 'TestPass123')
        print("✅ Demo user created successfully!")
    
    print("\n🌐 Available Routes:")
    print("   Web Interface:")
    print("   - http://localhost:5000/ (Home)")
    print("   - http://localhost:5000/register (Registration)")
    print("   - http://localhost:5000/login (Login)")
    print("   - http://localhost:5000/dashboard (Protected)")
    print("   - http://localhost:5000/profile (Protected)")
    print("\n   API Endpoints:")
    print("   - POST /api/register")
    print("   - POST /api/login")
    print("   - POST /api/logout")
    print("   - GET /api/status")
    print("   - GET /api/profile")
    
    app.run(debug=True, host='0.0.0.0', port=5000)