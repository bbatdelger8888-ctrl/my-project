import os
import sqlite3

from flask import (
    Flask, abort, flash, g, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

import scoring
from i18n import DEFAULT_LANG, LANGS, translate

SCHEMA = """
CREATE TABLE IF NOT EXISTS engineers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    specialty TEXT NOT NULL DEFAULT '',
    years REAL NOT NULL DEFAULT 0,
    academic TEXT NOT NULL DEFAULT 'none',
    professional TEXT NOT NULL DEFAULT 'none'
);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engineer_id INTEGER NOT NULL REFERENCES engineers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    deposit TEXT NOT NULL DEFAULT '',
    size TEXT NOT NULL,
    complexity TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engineer_id INTEGER NOT NULL REFERENCES engineers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    UNIQUE (engineer_id, name)
);
"""


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
        DATABASE=os.environ.get("DATABASE", os.path.join(app.instance_path, "engineers.db")),
    )
    if config:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    with app.app_context():
        get_db().executescript(SCHEMA)

    def lang():
        return session.get("lang", DEFAULT_LANG)

    @app.context_processor
    def inject():
        return {
            "t": lambda key: translate(lang(), key),
            "lang": lang(),
            "langs": LANGS,
            "current_user_id": session.get("user_id"),
            "s": scoring,
        }

    def engineer_score(db, eng):
        projects = db.execute("SELECT * FROM projects WHERE engineer_id = ?", (eng["id"],)).fetchall()
        skills = db.execute("SELECT * FROM skills WHERE engineer_id = ?", (eng["id"],)).fetchall()
        return projects, skills, scoring.total_score(eng, projects, skills)

    def require_login():
        uid = session.get("user_id")
        if uid is None:
            abort(redirect(url_for("login")))
        return uid

    @app.route("/lang/<code>")
    def set_lang(code):
        if code in LANGS:
            session["lang"] = code
        return redirect(request.referrer or url_for("index"))

    @app.route("/")
    def index():
        db = get_db()
        software = request.args.get("software", "")
        try:
            min_score = float(request.args.get("min_score") or 0)
        except ValueError:
            min_score = 0
        rows = []
        for eng in db.execute("SELECT * FROM engineers").fetchall():
            projects, skills, score = engineer_score(db, eng)
            if software and software not in {s["name"] for s in skills}:
                continue
            if score["total"] < min_score:
                continue
            rows.append({"eng": eng, "score": score, "n_projects": len(projects)})
        rows.sort(key=lambda r: r["score"]["total"], reverse=True)
        return render_template("index.html", rows=rows, software=software, min_score=min_score)

    @app.route("/engineer/<int:eng_id>")
    def engineer(eng_id):
        db = get_db()
        eng = db.execute("SELECT * FROM engineers WHERE id = ?", (eng_id,)).fetchone()
        if eng is None:
            abort(404)
        projects, skills, score = engineer_score(db, eng)
        return render_template("engineer.html", eng=eng, projects=projects, skills=skills, score=score)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            full_name = request.form.get("full_name", "").strip()
            if not email or not password or not full_name:
                flash(translate(lang(), "fill_required"))
            else:
                db = get_db()
                try:
                    cur = db.execute(
                        "INSERT INTO engineers (email, password_hash, full_name) VALUES (?, ?, ?)",
                        (email, generate_password_hash(password), full_name),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    flash(translate(lang(), "email_taken"))
                else:
                    session["user_id"] = cur.lastrowid
                    return redirect(url_for("profile"))
        return render_template("auth.html", mode="register")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            eng = get_db().execute("SELECT * FROM engineers WHERE email = ?", (email,)).fetchone()
            if eng and check_password_hash(eng["password_hash"], request.form.get("password", "")):
                session["user_id"] = eng["id"]
                return redirect(url_for("profile"))
            flash(translate(lang(), "invalid_login"))
        return render_template("auth.html", mode="login")

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("index"))

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        uid = require_login()
        db = get_db()
        if request.method == "POST":
            f = request.form
            try:
                years = max(0.0, float(f.get("years") or 0))
            except ValueError:
                years = 0.0
            academic = f.get("academic") if f.get("academic") in scoring.ACADEMIC_POINTS else "none"
            professional = f.get("professional") if f.get("professional") in scoring.PROFESSIONAL_POINTS else "none"
            db.execute(
                "UPDATE engineers SET full_name = ?, specialty = ?, years = ?, academic = ?, professional = ? WHERE id = ?",
                (f.get("full_name", "").strip() or "-", f.get("specialty", "").strip(), years, academic, professional, uid),
            )
            db.commit()
            flash(translate(lang(), "saved"))
            return redirect(url_for("profile"))
        eng = db.execute("SELECT * FROM engineers WHERE id = ?", (uid,)).fetchone()
        if eng is None:
            session.pop("user_id", None)
            return redirect(url_for("login"))
        projects, skills, score = engineer_score(db, eng)
        return render_template("profile.html", eng=eng, projects=projects, skills=skills, score=score)

    @app.route("/profile/projects", methods=["POST"])
    def add_project():
        uid = require_login()
        f = request.form
        name = f.get("name", "").strip()
        if name and f.get("size") in scoring.PROJECT_SIZES and f.get("complexity") in scoring.PROJECT_COMPLEXITIES:
            db = get_db()
            db.execute(
                "INSERT INTO projects (engineer_id, name, deposit, size, complexity) VALUES (?, ?, ?, ?, ?)",
                (uid, name, f.get("deposit", "").strip(), f["size"], f["complexity"]),
            )
            db.commit()
        else:
            flash(translate(lang(), "fill_required"))
        return redirect(url_for("profile"))

    @app.route("/profile/projects/<int:pid>/delete", methods=["POST"])
    def delete_project(pid):
        uid = require_login()
        db = get_db()
        db.execute("DELETE FROM projects WHERE id = ? AND engineer_id = ?", (pid, uid))
        db.commit()
        return redirect(url_for("profile"))

    @app.route("/profile/skills", methods=["POST"])
    def add_skill():
        uid = require_login()
        f = request.form
        if f.get("name") in scoring.SOFTWARE_LIST and f.get("level") in scoring.SOFTWARE_LEVELS:
            db = get_db()
            db.execute(
                "INSERT INTO skills (engineer_id, name, level) VALUES (?, ?, ?) "
                "ON CONFLICT (engineer_id, name) DO UPDATE SET level = excluded.level",
                (uid, f["name"], f["level"]),
            )
            db.commit()
        else:
            flash(translate(lang(), "fill_required"))
        return redirect(url_for("profile"))

    @app.route("/profile/skills/<int:sid>/delete", methods=["POST"])
    def delete_skill(sid):
        uid = require_login()
        db = get_db()
        db.execute("DELETE FROM skills WHERE id = ? AND engineer_id = ?", (sid, uid))
        db.commit()
        return redirect(url_for("profile"))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
