import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "quiniela-mundial-2026")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "mundial2026")
DB_PATH = os.path.join(os.path.dirname(__file__), "quiniela.db")

USERS = ["Adrian", "Gustavo", "Marcos", "Lillana", "Arnulfo", "Antonio"]

# (match_number, date, group, team1, team2)
MATCHES = [
    (1, "2026-06-11", "A", "México", "Sudáfrica"),
    (2, "2026-06-11", "A", "Corea del Sur", "Chequia"),
    (3, "2026-06-12", "B", "Canadá", "Bosnia y Herzegovina"),
    (4, "2026-06-12", "D", "Estados Unidos", "Paraguay"),
    (5, "2026-06-13", "C", "Haití", "Escocia"),
    (6, "2026-06-13", "D", "Australia", "Turquía"),
    (7, "2026-06-13", "C", "Brasil", "Marruecos"),
    (8, "2026-06-13", "B", "Catar", "Suiza"),
    (9, "2026-06-14", "E", "Costa de Marfil", "Ecuador"),
    (10, "2026-06-14", "E", "Alemania", "Curazao"),
    (11, "2026-06-14", "F", "Países Bajos", "Japón"),
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
    (25, "2026-06-18", "A", "Chequia", "Sudáfrica"),
    (26, "2026-06-18", "B", "Suiza", "Bosnia y Herzegovina"),
    (27, "2026-06-18", "B", "Canadá", "Catar"),
    (28, "2026-06-18", "A", "México", "Corea del Sur"),
    (29, "2026-06-19", "C", "Brasil", "Haití"),
    (30, "2026-06-19", "C", "Escocia", "Marruecos"),
    (31, "2026-06-19", "D", "Turquía", "Paraguay"),
    (32, "2026-06-19", "D", "Estados Unidos", "Australia"),
    (33, "2026-06-20", "E", "Alemania", "Costa de Marfil"),
    (34, "2026-06-20", "E", "Ecuador", "Curazao"),
    (35, "2026-06-20", "F", "Países Bajos", "Suecia"),
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
    (52, "2026-06-24", "B", "Bosnia y Herzegovina", "Catar"),
    (53, "2026-06-24", "A", "Chequia", "México"),
    (54, "2026-06-24", "A", "Sudáfrica", "Corea del Sur"),
    (55, "2026-06-25", "E", "Curazao", "Costa de Marfil"),
    (56, "2026-06-25", "E", "Ecuador", "Alemania"),
    (57, "2026-06-25", "F", "Japón", "Suecia"),
    (58, "2026-06-25", "F", "Túnez", "Países Bajos"),
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


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY,
        match_number INTEGER,
        date TEXT,
        group_name TEXT,
        team1 TEXT,
        team2 TEXT,
        score1 INTEGER,
        score2 INTEGER
    );
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        match_id INTEGER,
        pred1 INTEGER,
        pred2 INTEGER,
        UNIQUE(user, match_id)
    );
    """)
    count = db.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    if count == 0:
        db.executemany(
            "INSERT INTO matches (match_number, date, group_name, team1, team2) VALUES (?,?,?,?,?)",
            MATCHES,
        )
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


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        if user in USERS:
            session["user"] = user
            return redirect(url_for("predicciones"))
    return render_template("login.html", users=USERS)


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
                """INSERT INTO predictions (user, match_id, pred1, pred2)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(user, match_id) DO UPDATE SET pred1=excluded.pred1, pred2=excluded.pred2""",
                (user, match["id"], p1, p2),
            )
        db.commit()
        return redirect(url_for("predicciones"))

    matches = db.execute("SELECT * FROM matches ORDER BY match_number").fetchall()
    preds = {
        row["match_id"]: (row["pred1"], row["pred2"])
        for row in db.execute("SELECT * FROM predictions WHERE user = ?", (user,)).fetchall()
    }
    return render_template("predicciones.html", matches=matches, preds=preds, user=user)


@app.route("/tabla")
def tabla():
    db = get_db()
    matches = db.execute("SELECT * FROM matches").fetchall()
    all_preds = db.execute("SELECT * FROM predictions").fetchall()

    scores = {u: 0 for u in USERS}
    for pred in all_preds:
        match = next((m for m in matches if m["id"] == pred["match_id"]), None)
        if match is None:
            continue
        pts = calc_points(pred["pred1"], pred["pred2"], match["score1"], match["score2"])
        if pred["user"] in scores:
            scores[pred["user"]] += pts

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return render_template("tabla.html", ranking=ranking, user=session.get("user"))


@app.route("/resultados")
def resultados():
    db = get_db()
    matches = db.execute(
        "SELECT * FROM matches WHERE score1 IS NOT NULL ORDER BY match_number"
    ).fetchall()
    all_preds = db.execute("SELECT * FROM predictions").fetchall()

    preds_by_match = {}
    for pred in all_preds:
        preds_by_match.setdefault(pred["match_id"], {})[pred["user"]] = (
            pred["pred1"],
            pred["pred2"],
            calc_points(pred["pred1"], pred["pred2"], None, None),
        )

    rows = []
    for match in matches:
        user_preds = {}
        for u in USERS:
            entry = preds_by_match.get(match["id"], {}).get(u)
            if entry:
                p1, p2, _ = entry
                pts = calc_points(p1, p2, match["score1"], match["score2"])
                user_preds[u] = (p1, p2, pts)
            else:
                user_preds[u] = None
        rows.append((match, user_preds))

    return render_template("resultados.html", rows=rows, users=USERS, user=session.get("user"))


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


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
