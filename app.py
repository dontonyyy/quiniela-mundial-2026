import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "quiniela-mundial-2026")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "mundial2026")
DB_PATH = os.path.join(os.path.dirname(__file__), "quiniela.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

# (match_number, date, group, team1, team2)
MATCHES = [
    (1, "2026-06-11", "A", "México", "Sudáfrica"),
    (2, "2026-06-11", "A", "Corea del Sur", "República Checa"),
    (3, "2026-06-12", "B", "Canadá", "Bosnia y Herzegovina"),
    (4, "2026-06-12", "D", "Estados Unidos", "Paraguay"),
    (5, "2026-06-13", "C", "Haití", "Escocia"),
    (6, "2026-06-13", "D", "Australia", "Turquía"),
    (7, "2026-06-13", "C", "Brasil", "Marruecos"),
    (8, "2026-06-13", "B", "Qatar", "Suiza"),
    (9, "2026-06-14", "E", "Costa de Marfil", "Ecuador"),
    (10, "2026-06-14", "E", "Alemania", "Curazao"),
    (11, "2026-06-14", "F", "Holanda", "Japón"),
    (12, "2026-06-14", "F", "Suecia", "Túnez"),
    (13, "2026-06-15", "H", "Arabia Saudita", "Uruguay"),
    (14, "2026-06-15", "H", "España", "Cabo Verde"),
    (15, "2026-06-15", "G", "Irán", "Nueva Zelanda"),
    (16, "2026-06-15", "G", "Bélgica", "Egipto"),
    (17, "2026-06-16", "I", "Francia", "Senegal"),
    (18, "2026-06-16", "I", "Irak", "Noruega"),
    (19, "2026-06-16", "J", "Argentina", "Argelia"),
    (20, "2026-06-16", "J", "Austria", "Jordania"),
    (21, "2026-06-17", "L", "Ghana", "Panamá"),
    (22, "2026-06-17", "L", "Inglaterra", "Croacia"),
    (23, "2026-06-17", "K", "Portugal", "RD Congo"),
    (24, "2026-06-17", "K", "Uzbekistán", "Colombia"),
    (25, "2026-06-18", "A", "República Checa", "Sudáfrica"),
    (26, "2026-06-18", "B", "Suiza", "Bosnia y Herzegovina"),
    (27, "2026-06-18", "B", "Canadá", "Qatar"),
    (28, "2026-06-18", "A", "México", "Corea del Sur"),
    (29, "2026-06-19", "C", "Brasil", "Haití"),
    (30, "2026-06-19", "C", "Escocia", "Marruecos"),
    (31, "2026-06-19", "D", "Turquía", "Paraguay"),
    (32, "2026-06-19", "D", "Estados Unidos", "Australia"),
    (33, "2026-06-20", "E", "Alemania", "Costa de Marfil"),
    (34, "2026-06-20", "E", "Ecuador", "Curazao"),
    (35, "2026-06-20", "F", "Holanda", "Suecia"),
    (36, "2026-06-20", "F", "Túnez", "Japón"),
    (37, "2026-06-21", "H", "Uruguay", "Cabo Verde"),
    (38, "2026-06-21", "H", "España", "Arabia Saudita"),
    (39, "2026-06-21", "G", "Bélgica", "Irán"),
    (40, "2026-06-21", "G", "Nueva Zelanda", "Egipto"),
    (41, "2026-06-22", "I", "Noruega", "Senegal"),
    (42, "2026-06-22", "I", "Francia", "Irak"),
    (43, "2026-06-22", "J", "Argentina", "Austria"),
    (44, "2026-06-22", "J", "Jordania", "Argelia"),
    (45, "2026-06-23", "L", "Inglaterra", "Ghana"),
    (46, "2026-06-23", "L", "Panamá", "Croacia"),
    (47, "2026-06-23", "K", "Portugal", "Uzbekistán"),
    (48, "2026-06-23", "K", "Colombia", "RD Congo"),
    (49, "2026-06-24", "C", "Escocia", "Brasil"),
    (50, "2026-06-24", "C", "Marruecos", "Haití"),
    (51, "2026-06-24", "B", "Suiza", "Canadá"),
    (52, "2026-06-24", "B", "Bosnia y Herzegovina", "Qatar"),
    (53, "2026-06-24", "A", "República Checa", "México"),
    (54, "2026-06-24", "A", "Sudáfrica", "Corea del Sur"),
    (55, "2026-06-25", "E", "Curazao", "Costa de Marfil"),
    (56, "2026-06-25", "E", "Ecuador", "Alemania"),
    (57, "2026-06-25", "F", "Japón", "Suecia"),
    (58, "2026-06-25", "F", "Túnez", "Holanda"),
    (59, "2026-06-25", "D", "Turquía", "Estados Unidos"),
    (60, "2026-06-25", "D", "Paraguay", "Australia"),
    (61, "2026-06-26", "I", "Noruega", "Francia"),
    (62, "2026-06-26", "I", "Senegal", "Irak"),
    (63, "2026-06-26", "G", "Egipto", "Irán"),
    (64, "2026-06-26", "G", "Nueva Zelanda", "Bélgica"),
    (65, "2026-06-26", "H", "Cabo Verde", "Arabia Saudita"),
    (66, "2026-06-26", "H", "Uruguay", "España"),
    (67, "2026-06-27", "L", "Panamá", "Inglaterra"),
    (68, "2026-06-27", "L", "Croacia", "Ghana"),
    (69, "2026-06-27", "J", "Argelia", "Austria"),
    (70, "2026-06-27", "J", "Jordania", "Argentina"),
    (71, "2026-06-27", "K", "Colombia", "Portugal"),
    (72, "2026-06-27", "K", "RD Congo", "Uzbekistán"),
]


class DB:
    """Envoltorio fino que permite usar la misma sintaxis de consultas
    (placeholders '?') tanto con SQLite como con Postgres."""

    def __init__(self, conn, is_postgres):
        self.conn = conn
        self.is_postgres = is_postgres

    def execute(self, sql, params=()):
        if self.is_postgres:
            sql = sql.replace("?", "%s")
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def executemany(self, sql, seq):
        if self.is_postgres:
            sql = sql.replace("?", "%s")
        cur = self.conn.cursor()
        cur.executemany(sql, seq)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def connect_db():
    if DATABASE_URL:
        import psycopg2
        import psycopg2.extras

        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        return DB(conn, is_postgres=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return DB(conn, is_postgres=False)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = connect_db()
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = connect_db()

    if db.is_postgres:
        db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id SERIAL PRIMARY KEY,
                match_number INTEGER,
                date TEXT,
                group_name TEXT,
                team1 TEXT,
                team2 TEXT,
                score1 INTEGER,
                score2 INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                username TEXT,
                match_id INTEGER,
                pred1 INTEGER,
                pred2 INTEGER,
                UNIQUE(username, match_id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT,
                password_hash TEXT
            )
        """)
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_idx ON users (LOWER(username))")
    else:
        db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                match_number INTEGER,
                date TEXT,
                group_name TEXT,
                team1 TEXT,
                team2 TEXT,
                score1 INTEGER,
                score2 INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                match_id INTEGER,
                pred1 INTEGER,
                pred2 INTEGER,
                UNIQUE(username, match_id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password_hash TEXT
            )
        """)
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username_lower_idx ON users (LOWER(username))")

    count = db.execute("SELECT COUNT(*) AS cnt FROM matches").fetchone()["cnt"]
    if count == 0:
        db.executemany(
            "INSERT INTO matches (match_number, date, group_name, team1, team2) VALUES (?,?,?,?,?)",
            MATCHES,
        )
    else:
        renames = {"Chequia": "República Checa", "Catar": "Qatar", "Países Bajos": "Holanda"}
        for old, new in renames.items():
            db.execute("UPDATE matches SET team1=? WHERE team1=?", (new, old))
            db.execute("UPDATE matches SET team2=? WHERE team2=?", (new, old))
    db.commit()
    db.close()


def calc_points(pred1, pred2, score1, score2):
    if pred1 is None or pred2 is None or score1 is None or score2 is None:
        return 0
    if pred1 == score1 and pred2 == score2:
        return 3
    pred_result = (pred1 > pred2) - (pred1 < pred2)
    real_result = (score1 > score2) - (score1 < score2)
    if pred_result == real_result:
        return 1
    return 0


@app.context_processor
def inject_pending_today():
    user = session.get("user")
    if not user:
        return {}
    db = get_db()
    today = date.today().isoformat()
    pending = db.execute(
        """SELECT m.team1, m.team2 FROM matches m
           WHERE m.date = ?
           AND NOT EXISTS (
               SELECT 1 FROM predictions p WHERE p.match_id = m.id AND p.username = ?
           )
           ORDER BY m.match_number""",
        (today, user),
    ).fetchall()
    return {"pending_today": pending}


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
        if row and check_password_hash(row["password_hash"], password):
            session["user"] = row["username"]
            return redirect(url_for("predicciones"))
        error = "Usuario o contraseña incorrectos."
    return render_template("login.html", error=error)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            error = "Completa tu nombre y contraseña."
        elif len(password) < 4:
            error = "La contraseña debe tener al menos 4 caracteres."
        else:
            db = get_db()
            existing = db.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
            if existing:
                error = "Ese nombre ya está registrado, elige otro."
            else:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
                session["user"] = username
                return redirect(url_for("predicciones"))
    return render_template("registro.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/predicciones", methods=["GET", "POST"])
def predicciones():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    db = get_db()

    if request.method == "POST":
        matches = db.execute("SELECT * FROM matches").fetchall()
        for match in matches:
            if match["score1"] is not None:
                continue  # ya tiene resultado, no se puede modificar
            p1 = request.form.get(f"pred1_{match['id']}")
            p2 = request.form.get(f"pred2_{match['id']}")
            if p1 == "" or p2 == "" or p1 is None or p2 is None:
                continue
            try:
                p1, p2 = int(p1), int(p2)
            except ValueError:
                continue
            db.execute(
                """INSERT INTO predictions (username, match_id, pred1, pred2)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(username, match_id) DO UPDATE SET pred1=excluded.pred1, pred2=excluded.pred2""",
                (user, match["id"], p1, p2),
            )
        db.commit()
        return redirect(url_for("predicciones"))

    matches = db.execute("SELECT * FROM matches ORDER BY match_number").fetchall()
    preds = {
        row["match_id"]: (row["pred1"], row["pred2"])
        for row in db.execute("SELECT * FROM predictions WHERE username = ?", (user,)).fetchall()
    }
    return render_template("predicciones.html", matches=matches, preds=preds, user=user)


@app.route("/predicciones/guardar/<int:match_id>", methods=["POST"])
def predicciones_guardar(match_id):
    user = session.get("user")
    if not user:
        return {"ok": False, "error": "No autenticado"}, 403

    db = get_db()
    match = db.execute("SELECT score1 FROM matches WHERE id = ?", (match_id,)).fetchone()
    if match is None:
        return {"ok": False, "error": "Partido no encontrado"}, 404
    if match["score1"] is not None:
        return {"ok": False, "error": "Este partido ya tiene resultado cargado"}, 400

    p1 = request.form.get("pred1")
    p2 = request.form.get("pred2")
    if p1 in (None, "") or p2 in (None, ""):
        return {"ok": False, "error": "Completa ambos resultados"}, 400
    try:
        p1, p2 = int(p1), int(p2)
    except ValueError:
        return {"ok": False, "error": "Resultado inválido"}, 400

    db.execute(
        """INSERT INTO predictions (username, match_id, pred1, pred2)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(username, match_id) DO UPDATE SET pred1=excluded.pred1, pred2=excluded.pred2""",
        (user, match_id, p1, p2),
    )
    db.commit()
    return {"ok": True}


@app.route("/tabla")
def tabla():
    db = get_db()
    matches = db.execute("SELECT * FROM matches").fetchall()
    all_preds = db.execute("SELECT * FROM predictions").fetchall()
    users = [row["username"] for row in db.execute("SELECT username FROM users").fetchall()]

    scores = {u: 0 for u in users}
    for pred in all_preds:
        match = next((m for m in matches if m["id"] == pred["match_id"]), None)
        if match is None:
            continue
        pts = calc_points(pred["pred1"], pred["pred2"], match["score1"], match["score2"])
        if pred["username"] in scores:
            scores[pred["username"]] += pts

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return render_template("tabla.html", ranking=ranking, user=session.get("user"))


@app.route("/resultados")
def resultados():
    db = get_db()
    matches = db.execute(
        "SELECT * FROM matches WHERE score1 IS NOT NULL ORDER BY match_number"
    ).fetchall()
    all_preds = db.execute("SELECT * FROM predictions").fetchall()
    users = [row["username"] for row in db.execute("SELECT username FROM users").fetchall()]

    preds_by_match = {}
    for pred in all_preds:
        preds_by_match.setdefault(pred["match_id"], {})[pred["username"]] = (
            pred["pred1"],
            pred["pred2"],
            calc_points(pred["pred1"], pred["pred2"], None, None),
        )

    rows = []
    for match in matches:
        user_preds = {}
        for u in users:
            entry = preds_by_match.get(match["id"], {}).get(u)
            if entry:
                p1, p2, _ = entry
                pts = calc_points(p1, p2, match["score1"], match["score2"])
                user_preds[u] = (p1, p2, pts)
            else:
                user_preds[u] = None
        rows.append((match, user_preds))

    return render_template("resultados.html", rows=rows, users=users, user=session.get("user"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        if request.method == "POST" and request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html")

    db = get_db()

    if request.method == "POST":
        matches = db.execute("SELECT * FROM matches").fetchall()
        for match in matches:
            s1 = request.form.get(f"score1_{match['id']}")
            s2 = request.form.get(f"score2_{match['id']}")
            if s1 == "" or s2 == "" or s1 is None or s2 is None:
                db.execute("UPDATE matches SET score1=NULL, score2=NULL WHERE id=?", (match["id"],))
                continue
            try:
                s1, s2 = int(s1), int(s2)
            except ValueError:
                continue
            db.execute("UPDATE matches SET score1=?, score2=? WHERE id=?", (s1, s2, match["id"]))
        db.commit()
        return redirect(url_for("admin"))

    matches = db.execute("SELECT * FROM matches ORDER BY match_number").fetchall()
    return render_template("admin.html", matches=matches)


@app.route("/admin/guardar/<int:match_id>", methods=["POST"])
def admin_guardar(match_id):
    if not session.get("admin"):
        return {"ok": False, "error": "No autenticado"}, 403

    db = get_db()
    s1 = request.form.get("score1")
    s2 = request.form.get("score2")
    if s1 in (None, "") or s2 in (None, ""):
        db.execute("UPDATE matches SET score1=NULL, score2=NULL WHERE id=?", (match_id,))
        db.commit()
        return {"ok": True}
    try:
        s1, s2 = int(s1), int(s2)
    except ValueError:
        return {"ok": False, "error": "Resultado inválido"}, 400
    db.execute("UPDATE matches SET score1=?, score2=? WHERE id=?", (s1, s2, match_id))
    db.commit()
    return {"ok": True}


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
