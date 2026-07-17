from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'dev'  # use a strong secret in production

# -----------------
# DATABASE FUNCTION
# -----------------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='quizcraft',
        user='root',
        password=''  # change if you have a password
    )

# -----------------
# SIGNUP ROUTE
# -----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        if password != confirmPassword:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Email already registered!", "error")
            cursor.close()
            conn.close()
            return redirect(url_for('signup'))

        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password) VALUES (%s,%s,%s,%s)",
            (firstName, lastName, email, hashed_pw)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# -----------------
# LOGIN ROUTE
# -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['user_name'] = user['first_name']
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# -----------------
# DASHBOARD ROUTE
# -----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_name=session['user_name'])

# -----------------
# LOGOUT ROUTE
# -----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
