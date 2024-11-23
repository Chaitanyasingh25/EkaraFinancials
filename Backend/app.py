from flask import Flask, request, jsonify
from flask_cors import CORS
from validate_email_address import validate_email
from sqlalchemy.exc import IntegrityError
import jwt
import os


# Flask app initialization
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'pvhSecretKey@123'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Mock databases (replace with a real database in production)
users = []  # To store user data
applications = []  # To store application data

@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return response

# --- SIGNUP ROUTE ---
@app.route("/signup", methods=["POST"])
def signup():
    try:
        # Extracting data from request
        first_name = request.json.get('firstNm')
        last_name = request.json.get('LastNm')
        linkedin = request.json.get('linkedin')
        email = request.json.get('email')
        password = request.json.get('password')
        confirm_password = request.json.get('confirm_password')

        # Validations
        if not validate_email(email):
            return jsonify({"error": "Invalid email address"}), 400
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check if user already exists
        if any(user['email'] == email for user in users):
            return jsonify({"error": "Email is already registered"}), 409

        # Add user to the mock database
        users.append({
            "firstNm": first_name,
            "LastNm": last_name,
            "linkedin": linkedin,
            "email": email,
            "password": password
        })

        return jsonify({"message": "User registered successfully!"}), 200

    except Exception as e:
        print("Signup Error:", e)
        return jsonify({"error": "An error occurred during signup"}), 500


# --- LOGIN ROUTE ---
@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        # Find the user in the mock database
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)
        if user:
            # Generate JWT token
            token = jwt.encode({'email': user['email']}, app.config['SECRET_KEY'], algorithm='HS256')
            session['logged_in'] = True
            return jsonify({
                "message": "Login successful!",
                "token": token,
                "user": {"email": user['email'], "firstNm": user['firstNm']}
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 403

    except Exception as e:
        print("Login Error:", e)
        return jsonify({"error": "An error occurred during login"}), 500


# --- APPLY ROUTE ---
@app.route("/apply", methods=["POST"])
def apply():
    try:
        # Extract data from form
        email = request.form.get('email')
        linkedIn = request.form.get('linkedIn')
        phone_number = request.form.get('phoneNumber')
        education_background = request.form.get('educationBackground')
        experience = request.form.get('experience')

        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Invalid email address"}), 400

        # Extract files
        founder_video = request.files.get('founderVideo')
        demo_video = request.files.get('demoVideo')

        # Save uploaded files
        founder_video_path = None
        demo_video_path = None
        if founder_video:
            founder_video_path = os.path.join(app.config['UPLOAD_FOLDER'], founder_video.filename)
            founder_video.save(founder_video_path)
        if demo_video:
            demo_video_path = os.path.join(app.config['UPLOAD_FOLDER'], demo_video.filename)
            demo_video.save(demo_video_path)

        # Store application in the mock database
        applications.append({
            "email": email,
            "linkedIn": linkedIn,
            "phoneNumber": phone_number,
            "educationBackground": education_background,
            "experience": experience,
            "founderVideo": founder_video_path,
            "demoVideo": demo_video_path
        })

        return jsonify({"message": "Application submitted successfully!"}), 200

    except Exception as e:
        print("Application Error:", e)
        return jsonify({"error": "An error occurred during application submission"}), 500


if __name__ == '__main__':
    app.run(debug=True)