from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'dailyplannersecret'


# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------
def init_db():
    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_name TEXT NOT NULL,
            task_time TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------------
# HOME PAGE
# -------------------------------
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE user_id = ? AND task_name LIKE ?"
    params = [session['user_id'], f"%{search}%"]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY task_time"

    cursor.execute(query, params)
    tasks = cursor.fetchall()

    conn.close()

    return render_template('index.html', tasks=tasks)


# -------------------------------
# REGISTER
# -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('planner.db')
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()

            flash("Registration successful! Please login.")
            return redirect('/login')

        except:
            flash("Username already exists!")

        finally:
            conn.close()

    return render_template('register.html')


# -------------------------------
# LOGIN
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('planner.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]

            flash("Login successful!")
            return redirect('/')

        flash("Invalid username or password!")

    return render_template('login.html')


# -------------------------------
# LOGOUT
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect('/login')


# -------------------------------
# ADD TASK
# -------------------------------
@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect('/login')

    task_name = request.form['task']
    task_time = request.form['time']

    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (user_id, task_name, task_time) VALUES (?, ?, ?)",
        (session['user_id'], task_name, task_time)
    )

    conn.commit()
    conn.close()

    flash("Task added successfully!")
    return redirect('/')


# -------------------------------
# DELETE TASK
# -------------------------------
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session['user_id'])
    )

    conn.commit()
    conn.close()

    flash("Task deleted successfully!")
    return redirect('/')


# -------------------------------
# COMPLETE TASK
# -------------------------------
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (task_id, session['user_id'])
    )

    conn.commit()
    conn.close()

    flash("Task marked as completed!")
    return redirect('/')


# -------------------------------
# EDIT TASK
# -------------------------------
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('planner.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        updated_task = request.form['task']
        updated_time = request.form['time']

        cursor.execute(
            '''
            UPDATE tasks
            SET task_name = ?, task_time = ?
            WHERE id = ? AND user_id = ?
            ''',
            (updated_task, updated_time, task_id, session['user_id'])
        )

        conn.commit()
        conn.close()

        flash("Task updated successfully!")
        return redirect('/')

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session['user_id'])
    )

    task = cursor.fetchone()
    conn.close()

    return render_template('edit.html', task=task)


# -------------------------------
# RUN APPLICATION
# -------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)