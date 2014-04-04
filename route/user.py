import os
from flask import request, session, redirect, jsonify
from orm.user import User
from route import render_error
from sysweb_server_flask import app, SYS_ROOT


@app.route("/login", methods=["POST"])
def login():
    u = User.login(request.form.get("email"), request.form.get("password"))
    if u is not None:
        session["email"] = request.form.get("email")
        session["current_user"] = User.find_by_email(session["email"]).__dict__
        session["current_user"]["username"] = session["email"]
        session["root"] = SYS_ROOT + "/" + u.username + "/"
        if not os.path.isdir(session["root"]):
            os.mkdir(session["root"])
        return jsonify(**{"user": u.__dict__})
    else:
        return render_error("Login Error")


@app.route("/logout")
def logout():
    session.pop("current_user", None)
    session.pop("email", None)
    session.pop("root", None)
    return jsonify(**{"success": True})


@app.route("/register", methods=["POST"])
def register():
    if session.get("current_user"):
        return render_error("You have registered.")
    import smtplib

    email = request.form.get("email")
    password = request.form.get("password")
    u = User.find_one(username=email)
    if u:
        return render_error("You has already registered.")

    u = User(email=email,
             username=email,
             password=User.encrypt(password),
             code=User.encrypt("%s code %s" % (email, password))).save()

    if hasattr(u, u.Meta.primary):
        session["current_user"] = u.__dict__
        sender = "postmaster@abillist.com"
        recivers = [email, ]
        smtp_obj = smtplib.SMTP("smtp.abillist.com", 25)
        smtp_obj.login(sender, "1008_not")
        subject = "Account Active Mail"
        html = """
                Click <a href='http://%s/user/active?uid=%s&code=%s'>http://%s/user/active?uid=%s&code=%s</a> to active your account.
                <br> Your password: %s
               """ % ("sys.abillist.com", str(u.m_id), u.code, "sys.abillist.com", str(u.m_id), u.code, password)
        message = "\r\n".join([
            "From: " + sender,
            "MIME-Version: 1.0",
            "Content-type: text/html",
            "Subject: " + subject,
            "\r\n",
            html
        ])
        smtp_obj.sendmail(sender, recivers, message)
        return jsonify(**{"user": u.__dict__})
    else:
        return render_error("Register Error.")


@app.route("/user/active")
def active():
    uid = request.args.get("uid")
    code = request.args.get("code")
    u = User.find_by_id(int(uid))
    if not u:
        return render_error("Account not exists.")
    if code == u.code:
        u.enable = True
        u.save()
    if u.enable:
        session["email"] = u.username
        session["current_user"] = u.__dict__
        session["root"] = SYS_ROOT + "/" + u.username + "/"
        if not os.path.isdir(session["root"]):
            os.mkdir(session["root"])
        return redirect("")
    return render_error("Active Failed!")


@app.route("/user/current", methods=["GET", "POST"])
def current():
    print(session.get("current_user"))
    if "current_user" in session:
        return jsonify(**{"user": session.get("current_user")})
    else:
        return "Not Found", 404