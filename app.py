from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, time
import hashlib

app = Flask(__name__)
app.secret_key = "secret_demo"

# =========================
# KONFIGURASI ADMIN (DEMO)
# =========================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# =========================
# SETTING PEMILIHAN
# =========================
settings = {
    "wilayah": "Jatireja",
    "start": time(8, 0),
    "end": time(17, 0)
}

# =========================
# DATA VOTING (SIMULASI)
# =========================
voted_users = set()
votes = {"A": 0, "B": 0}

# =========================
# FUNGSI BANTUAN
# =========================
def hash_nik(nik):
    return hashlib.sha256(nik.encode()).hexdigest()

def status_voting():
    now = datetime.now().time()
    if now < settings["start"]:
        return "BELUM_DIMULAI"
    elif settings["start"] <= now <= settings["end"]:
        return "SEDANG_BERJALAN"
    else:
        return "SELESAI"

# =========================
# LANDING
# =========================
@app.route("/")
def landing():
    return render_template("landing.html")

# =========================
# WARGA
# =========================
@app.route("/warga/register", methods=["GET", "POST"])
def warga_register():
    if status_voting() != "SEDANG_BERJALAN":
        return render_template(
            "warga/status.html",
            message="Pemungutan suara belum dibuka atau sudah ditutup."
        )

    if request.method == "POST":
        nik = request.form["nik"]
        domisili = request.form["domisili"]
        nik_hash = hash_nik(nik)

        if settings["wilayah"].lower() not in domisili.lower():
            return render_template(
                "warga/status.html",
                message="Data tidak valid. Anda bukan warga wilayah pemilihan."
            )

        if nik_hash in voted_users:
            return render_template(
                "warga/status.html",
                message="Anda sudah menggunakan hak pilih."
            )

        return redirect(url_for("warga_vote", nik=nik))

    return render_template("warga/register.html")

@app.route("/warga/vote", methods=["GET", "POST"])
def warga_vote():
    nik = request.args.get("nik")
    nik_hash = hash_nik(nik)

    if nik_hash in voted_users:
        return render_template(
            "warga/status.html",
            message="Anda sudah melakukan voting."
        )

    if request.method == "POST":
        pilihan = request.form["pilihan"]
        votes[pilihan] += 1
        voted_users.add(nik_hash)
        return render_template("warga/sukses.html")

    return render_template("warga/vote.html")

@app.route("/warga/result")
def warga_result():
    if status_voting() != "SELESAI":
        return render_template(
            "warga/status.html",
            message="Hasil voting belum dapat ditampilkan."
        )

    return render_template(
        "warga/result.html",
        calon_a=votes["A"],
        calon_b=votes["B"]
    )

# =========================
# ADMIN (DENGAN PROTEKSI)
# =========================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == ADMIN_USERNAME and
            request.form["password"] == ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template(
                "admin/login.html",
                error="Username atau password salah"
            )

    return render_template("admin/login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    return render_template(
        "admin/dashboard.html",
        settings=settings,
        status=status_voting()
    )

@app.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        settings["wilayah"] = request.form["wilayah"]
        settings["start"] = time.fromisoformat(request.form["start"])
        settings["end"] = time.fromisoformat(request.form["end"])
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/settings.html", settings=settings)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# =========================
if __name__ == "__main__":
    app.run(debug=True)
