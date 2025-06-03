from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('fitness.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists', 'error')
            conn.close()
            return render_template('signup.html')
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    # Fetch summary data
    total_workout = conn.execute('SELECT SUM(duration) as total FROM workouts WHERE user_id = ?',
                                (session['user_id'],)).fetchone()['total'] or 0
    total_calories = conn.execute('SELECT SUM(calories) as total FROM nutrition WHERE user_id = ?',
                                 (session['user_id'],)).fetchone()['total'] or 0
    avg_sleep = conn.execute('SELECT AVG(hours) as avg FROM sleep WHERE user_id = ?',
                            (session['user_id'],)).fetchone()['avg'] or 0
    total_water = conn.execute('SELECT SUM(glasses) as total FROM water WHERE user_id = ?',
                              (session['user_id'],)).fetchone()['total'] or 0
    conn.close()
    # Define goals for progress bars
    goals = {
        'workout': 150,  # 150 minutes of weekly workouts
        'calories': 2000,  # 2000 calories daily
        'sleep': 8,  # 8 hours of sleep daily
        'water': 8  # 8 glasses of water daily
    }
    summary = {
        'total_workout': total_workout,
        'total_calories': total_calories,
        'avg_sleep': round(avg_sleep, 1),
        'total_water': total_water,
        'goals': goals
    }
    return render_template('dashboard.html', summary=summary)

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        exercise = request.form['exercise']
        duration = request.form['duration']
        date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        conn.execute('INSERT INTO workouts (user_id, exercise, duration, date) VALUES (?, ?, ?, ?)',
                     (session['user_id'], exercise, duration, date))
        conn.commit()
        conn.close()
        flash('Workout logged!', 'success')
    conn = get_db_connection()
    workouts = conn.execute('SELECT * FROM workouts WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('workout.html', workouts=workouts)

@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        food = request.form['food']
        calories = request.form['calories']
        date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        conn.execute('INSERT INTO nutrition (user_id, food, calories, date) VALUES (?, ?, ?, ?)',
                     (session['user_id'], food, calories, date))
        conn.commit()
        conn.close()
        flash('Nutrition logged!', 'success')
    conn = get_db_connection()
    nutrition_logs = conn.execute('SELECT * FROM nutrition WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('nutrition.html', nutrition_logs=nutrition_logs)

@app.route('/sleep', methods=['GET', 'POST'])
def sleep():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        hours = request.form['hours']
        date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        conn.execute('INSERT INTO sleep (user_id, hours, date) VALUES (?, ?, ?)',
                     (session['user_id'], hours, date))
        conn.commit()
        conn.close()
        flash('Sleep logged!', 'success')
    conn = get_db_connection()
    sleep_logs = conn.execute('SELECT * FROM sleep WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('sleep.html', sleep_logs=sleep_logs)

@app.route('/water', methods=['GET', 'POST'])
def water():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        glasses = request.form['glasses']
        date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db_connection()
        conn.execute('INSERT INTO water (user_id, glasses, date) VALUES (?, ?, ?)',
                     (session['user_id'], glasses, date))
        conn.commit()
        conn.close()
        flash('Water intake logged!', 'success')
    conn = get_db_connection()
    water_logs = conn.execute('SELECT * FROM water WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('water.html', water_logs=water_logs)

@app.route('/calories')
def calories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    nutrition_logs = conn.execute('SELECT * FROM nutrition WHERE user_id = ?', (session['user_id'],)).fetchall()
    total_calories = sum(log['calories'] for log in nutrition_logs)
    conn.close()
    return render_template('calories.html', total_calories=total_calories)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)