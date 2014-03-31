import base64
import os
from flask import request, \
    render_template, \
    make_response, \
    session, \
    redirect, \
    url_for, \
    jsonify
from orm.user import User
from sysweb_server_flask import app, SYS_ROOT


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        u = User.login(request.form.get("email"), request.form.get("password"))
        if u is not None:
            session["email"] = request.form.get("email")
            session["current_user"] = User.find_by_email(session["email"]).__dict__
            session["current_user"]["username"] = session["email"]
            session["root"] = SYS_ROOT + "/" + u.username + "/"
            if not os.path.isdir(session["root"]):
                os.mkdir(session["root"])
            resp = jsonify(**{"user": u.__dict__})
        else:
            resp = make_response(render_template("login.html"))

        return resp


@app.route("/logout")
def logout():
    session.pop("current_user", None)
    session.pop("email", None)
    session.pop("root", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        if session.get("current_user"):
            return jsonify(**{
                "error": True,
                "message": "you have registered."
            })
        import smtplib

        email = request.form.get("email")
        password = request.form.get("password")

        u = User.find_one(username=email)

        if u:
            return jsonify(**{
                "error": True,
                "message": "You has already registered."
            })

        u = User(email=email,
                 username=email,
                 password=User.encrypt(password),
                 code=base64.urlsafe_b64decode(User.encrypt(email + password)))
        u.save()

        if hasattr(u, u.Meta.primary):
            session["current_user"] = u.__dict__
            sender = "postmaster@abillist.com"
            recivers = [email, ]
            smtp_obj = smtplib.SMTP("smtp.abillist.com", 25)
            smtp_obj.login(sender, "1008_not")
            subject = "Account Active Mail"
            html = """
                    Click <a href='http://%s/user/active?uid=%s&code=%s'>http://%s/user/active?uid=%s&code=%s</a>
                    to active your account.
                    <br>
                    Your password: %s
                    """ % ("sys.abillist.com", u.m_id, u.code, "sys.abillist.com", u.m_id, u.code, password)
            message = "\r\n".join([
                "From: " + sender,
                "MIME-Version: 1.0",
                "Content-type: text/html",
                "Subject: " + subject,
                "\r\n",
                html
            ])
            smtp_obj.sendmail(sender, recivers, message)
            print("Send mail successfully")
            return jsonify(**{
                "user": u.__dict__
            })
        return render_template("register.html")


@app.route("/user/active")
def active():
    uid = request.args.get("uid")
    code = request.args.get("code")
    u = User.find_by_id(int(uid))

    if not u:
        return jsonify(**{
            "error": True,
            "message": "Account not exists."
        })

    resp = "%d : %s , %r" % (int(uid), str(code), u.enable)
    if code == u.code:
        u.enable = True
        u.save()
    if u.enable:
        session["email"] = u.username
        session["current_user"] = u.__dict__
        session["root"] = SYS_ROOT + "/" + u.username + "/"
        if not os.path.isdir(session["root"]):
            os.mkdir(session["root"])
        if not os.path.exists(os.path.join(session["root"], "__sys.js")):
            open(os.path.join(session["root"], "__sys.js"), "w")
        return redirect("")
    return resp + "\n" + ("%d : %s , %r" % (int(uid), str(code), u.enable))


@app.route("/user/current", methods=["GET", "POST"])
def current():
    print(session.get("current_user"))
    if "current_user" in session:
        return jsonify(**{"user": session.get("current_user")})
    else:
        return "Not Found", 404