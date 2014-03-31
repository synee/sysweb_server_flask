from functools import wraps
import os, shutil
from flask import request, session, jsonify, g, redirect, url_for
from sysweb_server_flask import app


def login_required():
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("current_user") is None or not session.get("current_user")["enable"]:
                return jsonify(**{
                    "error": True,
                    "message": "login required."
                })
            return f(*args, **kwargs)

        return decorated_function

    return wrapper


def get_path(name="path"):
    if name in request.form:
        path = session["root"] + request.form[name]
    elif name in request.args:
        path = session["root"] + request.args[name]
    else:
        path = session["root"]
    return path.replace("//", "/")


def get_abs_path(f_path):
    return f_path.replace(session["root"], "/").replace("//", "/")


def get_parent_abs_path(f_path):
    return (os.path.dirname(f_path) + "/").replace(session["root"], "/").replace("//", "/")


def file_2_info(f_path):
    return {
        "name": os.path.basename(f_path),
        "file": os.path.isfile(f_path),
        "directory": os.path.isdir(f_path),
        "exists": os.path.exists(f_path),
        "absolutePath": get_abs_path(f_path),
        "parent": get_parent_abs_path(f_path),
        "create": os.path.getctime(f_path) if os.path.exists(f_path) else None,
        "modify": os.path.getmtime(f_path) if os.path.exists(f_path) else None,
        "size": os.path.getsize(f_path) if os.path.exists(f_path) else None
    }


def check_path(exists=[], not_exists=[], is_file=[], is_dir=[]):
    def check(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for f in exists:
                if not os.path.exists(get_path(f)):
                    return jsonify(**{
                        "error": True,
                        "message": "%s is not exists" % get_abs_path(get_path(f))
                    })
            for f in not_exists:
                if os.path.exists(get_path(f)):
                    return jsonify(**{
                        "error": True,
                        "message": "%s is exists" % get_abs_path(get_path(f))
                    })
            for f in is_file:
                if not os.path.isfile(get_path(f)):
                    return jsonify(**{
                        "error": True,
                        "message": "%s is not a file" % get_abs_path(get_path(f))
                    })
            for f in is_dir:
                if not os.path.isdir(get_path(f)):
                    return jsonify(**{
                        "error": True,
                        "message": "%s is not a directory" % get_abs_path(get_path(f))
                    })
            return func(*args, **kwargs)

        return wrapper

    return check


@app.route("/fs/cd")
@check_path(is_dir=["path"])
def cd():
    return jsonify(**file_2_info(get_path()))


@app.route("/fs/ls", methods=["GET"])
@login_required()
@check_path(is_dir=["path"])
def ls():
    return jsonify(**{
        "list": [file_2_info((get_path() + "/" + fname).replace("//", "/")) for fname in os.listdir(get_path())]
    })


@app.route("/fs/touch", methods=["POST"])
@login_required()
@check_path(not_exists=["path"])
def touch():
    open(get_path(), "w")
    return jsonify(**file_2_info(get_path()))


@app.route("/fs/stat")
@login_required()
@check_path(exists=["path"])
def stat():
    return jsonify(**file_2_info(get_path()))


@app.route("/fs/read", methods=["POST"])
@login_required()
@check_path(is_file=["path"])
def read():
    f_info = file_2_info(get_path())
    f_info["text"] = open(get_path()).read()
    return jsonify(**f_info)


@app.route("/fs/write", methods=["POST"])
@login_required()
@check_path(is_file=["path"])
def write():
    with open(get_path(), "w") as f:
        f.write(request.form["text"])
        f.close()
    f_info = file_2_info(get_path())
    f_info["text"] = open(get_path()).read()
    return jsonify(**f_info)


@app.route("/fs/append", methods=["POST"])
@login_required()
@check_path(is_file=["path"])
def append():
    with open(get_path(), "a") as f:
        f.write(request.form["text"])
        f.close()
    f_info = file_2_info(get_path())
    f_info["text"] = open(get_path()).read()
    return jsonify(**f_info)


@app.route("/fs/echo")
@login_required()
@check_path(is_file=["path"])
def echo():
    with open(get_path(), "a") as f:
        f.write("\n")
        f.write(request.form["text"])
        f.close()
    f_info = file_2_info(get_path())
    f_info["text"] = open(get_path()).read()
    return jsonify(**f_info)


@app.route("/fs/mkdir", methods=["POST"])
@login_required()
@check_path(not_exists=["path"])
def mkdir():
    os.mkdir(get_path())
    return jsonify(**file_2_info(get_path()))


@app.route("/fs/rm", methods=["POST"])
@login_required()
@check_path(exists=["path"])
def rm():
    if get_abs_path(get_path()) == "__sys.js":
        return jsonify(**{
            "error": True,
            "message": "This file cannot be removed."
        })
    if os.path.isdir(get_path()):
        os.removedirs(get_path())
    elif os.path.isfile(get_path()):
        os.remove(get_path())
    else:
        os.remove(get_path())

    return jsonify(**file_2_info(get_path()))


@app.route("/fs/cp", methods=["POST"])
@login_required()
@check_path(exists=["source"], not_exists=["dest"])
def cp():
    abs_parent_dir = (session["root"] + get_parent_abs_path(get_path("dest"))).replace("//", "/")
    if os.path.isfile(abs_parent_dir[:(len(abs_parent_dir) - 1)]):
        return jsonify(**{
            "error": True,
            "message": "%s is a file" % get_abs_path(abs_parent_dir)
        })
    if not os.path.isdir(abs_parent_dir):
        os.mkdir(abs_parent_dir)
    if os.path.isdir(get_path("source")):
        shutil.copytree(get_path("source"), get_path("dest"))
    else:
        shutil.copyfile(get_path("source"), get_path("dest"))

    return jsonify(**{
        "source": file_2_info(get_path("source")),
        "dest": file_2_info(get_path("dest"))
    })


@app.route("/fs/mv", methods=["POST"])
@login_required()
@check_path(exists=["source"], not_exists=["dest"])
def mv():
    if get_abs_path(get_path("source")) == "__sys.js":
        return jsonify(**{
            "error": True,
            "message": "This file cannot be removed."
        })

    shutil.move(get_path("source"), get_path("dest"))
    return jsonify(**{
        "source": file_2_info(get_path("source")),
        "dest": file_2_info(get_path("dest"))
    })


@app.route("/fs/head")
@login_required()
@check_path(is_file=["path"])
def head():
    f = open(get_path())
    f_info = file_2_info(get_path())
    f_info["text"] = "".join([f.readline() for i in range(0, 10)])
    return jsonify(**f_info)


@app.route("/fs/tail", methods=["POST"])
@login_required()
@check_path(is_file=["path"])
def tail():
    f = open(get_path())
    f_info = file_2_info(get_path())
    f_info["text"] = "".join(f.readlines()[-10:])
    return jsonify(**f_info)


