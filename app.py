import os, time, pymysql
from flask import Flask, request, redirect, render_template_string

pw = open(os.getenv("DB_PASSWORD_FILE", "/run/secrets/db_password")).read().strip()
app = Flask(__name__)

def db():
    return pymysql.connect(host="db", user="notes_user", password=pw, database="notesdb", autocommit=True, cursorclass=pymysql.cursors.DictCursor)

def init_db():
    for _ in range(30):
        try:
            c = db()
            c.cursor().execute("CREATE TABLE IF NOT EXISTS notes (id INT AUTO_INCREMENT PRIMARY KEY, content TEXT NOT NULL)")
            c.close()
            return
        except Exception as e:
            print("Waiting for DB...", e)
            time.sleep(2)

PAGE = """<h1>Notes App (Docker + Flask + MySQL)</h1>
<form method="post" action="/add"><input name="content" required><button>Add</button></form>
<ul>{% for n in notes %}<li>{{ n.content }}</li>{% endfor %}</ul>"""

@app.route("/")
def index():
    c = db(); cur = c.cursor()
    cur.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cur.fetchall(); c.close()
    return render_template_string(PAGE, notes=notes)

@app.route("/add", methods=["POST"])
def add():
    c = db()
    c.cursor().execute("INSERT INTO notes (content) VALUES (%s)", (request.form["content"],))
    c.close()
    return redirect("/")

init_db()
app.run(host="0.0.0.0", port=5000)
