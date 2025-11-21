from flask import Flask, request, jsonify, render_template, session
from passlib.hash import argon2
import mysql.connector
import os, random
from flask_mail import Mail, Message

app = Flask(__name__, template_folder="templates")
PEPPER = os.environ.get("PASSWORD_PEPPER", "")
app.secret_key = "Rahul!@#12346362662037"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "rwali4257@gmail.com"
app.config['MAIL_PASSWORD'] = "jhxlfqubqfxmxtsy"
mail = Mail(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/forgot")
def forget():
    return render_template("forgot.html")

@app.route("/verify")
def verify():
    return render_template("verify.html")

@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")

# Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="nagaraj",
        database="Skin_disease"
    )

# Create users table if not exists
db = get_connection()
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(100),
    otp VARCHAR(10) NULL
)
""")
db.commit()
cursor.close()
db.close()


# ✅ Register User API
@app.post("/register")
def register_user():
    data = request.json
    username = data["username"]
    email = data["email"]
    password = data["password"]

    to_hash = password + PEPPER
    password_hash = argon2.hash(to_hash)

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password_hash))
        db.commit()

        return jsonify({"success": True, "message": "User registered successfully!"})

    except mysql.connector.Error as err:
        if "Duplicate" in str(err):
            return jsonify({"success": False, "message": "Username or Email already exists!"})
        return jsonify({"success": False, "message": str(err)})

    finally:
        cursor.close()
        db.close()


# ✅ Login / Validate User API
@app.post("/login")
def login_user():
    data = request.json
    username = data["username"]
    password = data["password"]

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()

    cursor.close()
    db.close()

    if not row:
        return jsonify({"success": False, "message": "Invalid username or password"})

    stored_hash = row[0]

    if argon2.verify(password + PEPPER, stored_hash):
        return jsonify({"success": True, "message": "Login Successful!"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

@app.post("/forgot")
def forgot_password():
    data = request.json
    email = data["email"]
    
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": "Email is not registered!"})
    
    otp = str(random.randint(100000, 999999))

    cursor.execute("UPDATE users SET otp=%s WHERE email=%s", (otp, email))
    db.commit()

    # ✅ Save email in session
    session["email"] = email  

    msg = Message("Password Reset OTP", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"Your OTP for resetting password is: {otp}"
    mail.send(msg)

    cursor.close()
    db.close()

    return jsonify({"success": True, "message": "OTP sent to email"})

@app.post("/verify")
def verify_otp():
    data = request.json
    entered_otp = data["otp"]

    email = session.get("email")
    if not email:
        return jsonify({"success": False, "message": "Session expired. Please try again."})

    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT otp FROM users WHERE email=%s", (email,))
    stored_otp = cursor.fetchone()

    if stored_otp and stored_otp[0] == entered_otp:
        session["verified"] = True
        return jsonify({"success": True, "message": "OTP verified"})
    else:
        return jsonify({"success": False, "message": "Invalid OTP"})
    
@app.post("/reset_password")
def reset_password_action():
    if not session.get("verified"):
        return jsonify({"success": False, "message": "OTP not verified!"})

    data = request.json
    new_password = data["new_password"]

    email = session.get("email")

    password_hash = argon2.hash(new_password + PEPPER)

    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET password_hash=%s, otp=NULL WHERE email=%s",
                   (password_hash, email))
    db.commit()
    cursor.close()
    db.close()

    # ✅ Clear session to prevent reuse:
    session.pop("verified", None)
    session.pop("email", None)
    return jsonify({"success": True, "message": "Password changed successfully!"})

# ✅ Delete User API
@app.delete("/delete/<username>")
def delete_user(username):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "User deleted (if existed)."})


if __name__ == "__main__":
    app.run(debug=True)