from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

from ev_sys_pwa.app.utils.database.utils import get_user

app = Flask(__name__)

app.secret_key = 'abcdefghijklmn'
app.permanent_session_lifetime = timedelta(minutes=3)


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        id_ = request.form.get("id")
        password = request.form.get('pass')

        user = get_user(id_)
        if user and user.authenticated(password):
            session["id"] = user.username
            return redirect(url_for("login_"))
        else:
            return render_template("index.html")
    else:
        if "id" in session:
            return redirect(url_for("login_"))
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login_():
    if "id" in session:
        return render_template("login.html", id=session["id"])
    return render_template("index.html")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop('id', None)
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

