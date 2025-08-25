# User Authentication & Session Management App

A comprehensive Flask-based backend application that provides secure user authentication, session management, and protected routes with both web interface and REST API endpoints.

## 🚀 Features

### Core Functionality
- **User Registration**: Secure user registration with input validation
- **User Login/Logout**: Session-based authentication system
- **Protected Routes**: Access control for authenticated users only
- **Password Security**: Bcrypt hashing for secure password storage
- **Input Validation**: Comprehensive validation for usernames, emails, and passwords

### Security Features
- Strong password requirements (8+ chars, uppercase, lowercase, numbers)
- Email format validation
- Username uniqueness validation
- Session-based authentication with secure session handling
- SQL injection protection with parameterized queries
- CSRF protection through Flask's built-in mechanisms

### User Interface
- Clean, responsive web interface
- Registration and login forms
- Protected dashboard for authenticated users
- User profile page
- Error handling with user-friendly messages

### API Endpoints
- RESTful API for programmatic access
- JSON request/response format
- Status checking endpoints
- Complete CRUD operations for user management

## 🛠️ Tech Stack

- **Language**: Python 3.7+
- **Framework**: Flask 2.3.3
- **Database**: SQLite (file-based, no setup required)
- **Password Hashing**: Werkzeug (bcrypt-based)
- **Session Management**: Flask-Session (server-side sessions)
- **Validation**: Custom regex-based validation
- **Security**: Built-in Flask security features

## 📦 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd user-authentication-app
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Alternative: Direct Run
```bash
pip install Flask Werkzeug
python app.py
```

## 🔐 Demo Credentials

A test user is automatically created when you first run the application:

- **Username**: `testuser`
- **Email**: `test@example.com`
- **Password**: `TestPass123`

You can use these credentials to test the login functionality immediately.

## 🌐 Available Routes

### Web Interface Routes

| Route | Method | Description | Protection |
|-------|--------|-------------|------------|
| `/` | GET | Home page with navigation | Public |
| `/register` | GET/POST | User registration form | Public |
| `/login` | GET/POST | User login form | Public |
| `/logout` | GET | User logout | Public |
| `/dashboard` | GET | User dashboard | Protected |
| `/profile` | GET | User profile page | Protected |

### API Endpoints

| Endpoint | Method | Description | Protection | Request Body |
|----------|--------|-------------|------------|--------------|
| `/api/register` | POST | Create new user account | Public | `{username, email, password}` |
| `/api/login` | POST | Authenticate user | Public | `{email, password}` |
| `/api/logout` | POST | End user session | Public | None |
| `/api/status` | GET | Check authentication status | Public | None |
| `/api/profile` | GET | Get user profile data | Protected | None |

## 📝 API Usage Examples

### Registration
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@example.com", "password": "SecurePass123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123"}' \
  -c cookies.txt
```

### Access Protected Route
```bash
curl -X GET http://localhost:5000/api/profile \
  -b cookies.txt
```

### Check Authentication Status
```bash
curl -X GET http://localhost:5000/api/status \
  -b cookies.txt
```

### Logout
```bash
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

## 🔒 Password Requirements

For security, passwords must meet the following criteria:
- Minimum 8 characters long
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)

## 🗄️ Database Schema

The application uses SQLite with the following user table structure:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛡️ Security Features

### Input Validation
- **Email Validation**: Regex-based email format checking
- **Username Validation**: Alphanumeric characters and underscores only, minimum 3 characters
- **Password Strength**: Enforced complexity requirements
- **Input Sanitization**: Automatic trimming and normalization

### Authentication Security
- **Password Hashing**: Werkzeug's secure password hashing (bcrypt-based)
- **Session Management**: Server-side sessions with secure cookies
- **Session Timeout**: 24-hour session expiration
- **Brute Force Protection**: Failed login attempts handling

### Database Security
- **SQL Injection Prevention**: Parameterized queries throughout
- **Data Integrity**: Unique constraints on usernames and emails
- **Secure Storage**: No plaintext passwords stored

### Application Security
- **Secret Key**: Cryptographically secure session secret
- **HTTPS Ready**: Can be easily configured for HTTPS deployment
- **Error Handling**: Secure error messages that don't leak sensitive information

## 🚀 Deployment Options

### Free Hosting Platforms

#### 1. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### 2. Render
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`

#### 3. Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
```

#### 4. PythonAnywhere
1. Upload your code to PythonAnywhere
2. Set up a web app with Flask
3. Configure WSGI file to point to your app

### Environment Variables for Production
For production deployment, consider setting these environment variables:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-super-secret-key-here
export DATABASE_URL=your-database-url  # if using external database
```

## 🧪 Testing

### Manual Testing Checklist

#### Registration Testing
- [ ] Register with valid credentials
- [ ] Try registering with weak password
- [ ] Try registering with invalid email
- [ ] Try registering with existing email
- [ ] Try registering with existing username

#### Login Testing
- [ ] Login with valid credentials
- [ ] Try login with invalid email
- [ ] Try login with wrong password
- [ ] Try accessing protected routes without login

#### Session Management
- [ ] Check session persistence after login
- [ ] Test logout functionality
- [ ] Try accessing protected routes after logout

### Automated Testing Example
```python
import requests

base_url = "http://localhost:5000"

# Test registration
response = requests.post(f"{base_url}/api/register", json={
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "TestPass123"
})
print(f"Registration: {response.status_code}")

# Test login
session = requests.Session()
response = session.post(f"{base_url}/api/login", json={
    "email": "test2@example.com",
    "password": "TestPass123"
})
print(f"Login: {response.status_code}")

# Test protected route
response = session.get(f"{base_url}/api/profile")
print(f"Profile access: {response.status_code}")
```

## 📁 Project Structure

```
user-authentication-app/
│
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── users.db              # SQLite database (created automatically)
│
└── templates/            # HTML templates (embedded in app.py)
    ├── home.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    └── profile.html
```

## 🔧 Configuration Options

### Session Configuration
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session timeout
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only (for production)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
```

### Database Configuration
```python
# For production, consider using PostgreSQL or MySQL
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
```

## 🐛 Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install Flask
```

#### Database file permissions error
```bash
chmod 664 users.db
```

#### Session not persisting
- Check if cookies are enabled in your browser
- Ensure you're not in incognito/private mode
- For API testing, make sure to include cookies in subsequent requests

#### Port already in use
```python
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## 🔄 Future Enhancements

### Potential Features to Add
- **Email Verification**: Send confirmation emails for new registrations
- **Password Reset**: Forgot password functionality
- **Two-Factor Authentication**: SMS or app-based 2FA
- **User Roles**: Admin/user role-based access control
- **Profile Updates**: Allow users to update their information
- **Account Deletion**: Self-service account removal
- **Login History**: Track user login attempts and history
- **API Rate Limiting**: Prevent abuse of API endpoints

### Security Improvements
- **JWT Tokens**: Alternative to session-based auth
- **OAuth Integration**: Google/GitHub/Facebook login
- **Account Lockout**: Temporary lockout after failed attempts
- **Password History**: Prevent password reuse
- **CAPTCHA**: Bot protection for registration/login

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include error messages and steps to reproduce

## 🙏 Acknowledgments

- Flask framework and community
- Werkzeug for security utilities
- SQLite for the lightweight database solution
- The Python community for excellent documentation and resources

---

**Happy Coding! 🚀**