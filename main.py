from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secret key for Flask sessions

DATABASE = 'forum.db'



def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/init_db")
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        -- Create the threads table
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        -- Create the replies table
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            reports INTEGER DEFAULT 0,
            FOREIGN KEY (thread_id) REFERENCES threads (id)
        );

        -- Create the users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            badges TEXT DEFAULT ''
        );
    ''')
    conn.commit()
    conn.close()
    return "Database initialized!"





@app.route("/")
def view_threads():
    conn = get_db()
    threads = conn.execute("SELECT * FROM threads").fetchall()
    conn.close()
    return render_template("index.html", threads=threads)





@app.route("/create_thread", methods=["GET", "POST"])
def create_thread():
    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        conn.execute("INSERT INTO threads (title, category, created_at) VALUES (?, ?, ?)",
                     (title, category, created_at))
        conn.commit()
        conn.close()

        flash("Thread created successfully!")
        return redirect(url_for("view_threads"))
    return render_template("create_thread.html")





@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    conn = get_db()
    thread = conn.execute("SELECT * FROM threads WHERE id = ?", (thread_id,)).fetchone()
    replies = conn.execute("SELECT * FROM replies WHERE thread_id = ?", (thread_id,)).fetchall()
    conn.close()
    return render_template("thread.html", thread=thread, replies=replies)







@app.route("/reply/<int:thread_id>", methods=["POST"])
def add_reply(thread_id):
    content = request.form["content"]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    conn.execute("INSERT INTO replies (thread_id, content, created_at) VALUES (?, ?, ?)",
                 (thread_id, content, created_at))
    conn.commit()
    conn.close()

    flash("Reply added successfully!")
    return redirect(url_for("view_thread", thread_id=thread_id))











@app.route("/like/<int:reply_id>", methods=["POST"])
def like_reply(reply_id):
    conn = get_db()
    conn.execute("UPDATE replies SET likes = likes + 1 WHERE id = ?", (reply_id,))
    conn.commit()
    conn.close()
    flash("Reply liked!")
    return redirect(request.referrer)





@app.route("/report/<int:reply_id>", methods=["POST"])
def report_reply(reply_id):
    conn = get_db()
    conn.execute("UPDATE replies SET reports = reports + 1 WHERE id = ?", (reply_id,))
    conn.commit()
    conn.close()
    flash("Reply reported!")
    return redirect(request.referrer)



@app.route("/admin/delete_thread/<int:thread_id>", methods=["POST"])
def delete_thread(thread_id):
    conn = get_db()
    conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
    conn.execute("DELETE FROM replies WHERE thread_id = ?", (thread_id,))
    conn.commit()
    conn.close()
    flash("Thread deleted!")
    return redirect(url_for("view_threads"))



@app.route("/admin/delete_reply/<int:reply_id>", methods=["POST"])
def delete_reply(reply_id):
    conn = get_db()
    conn.execute("DELETE FROM replies WHERE id = ?", (reply_id,))
    conn.commit()
    conn.close()
    flash("Reply deleted!")
    return redirect(request.referrer)



@app.route("/assign_badge/<int:user_id>", methods=["POST"])
def assign_badge(user_id):
    badge = request.form["badge"]

    conn = get_db()
    conn.execute("UPDATE users SET badges = badges || ? WHERE id = ?", (f"{badge}, ", user_id))
    conn.commit()
    conn.close()

    flash("Badge assigned!")
    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(debug=True)
