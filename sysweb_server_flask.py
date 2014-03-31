import os
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
app = Flask(__name__,
            static_url_path="",
            static_folder=STATIC_DIR
)


SYS_ROOT = os.path.join(STATIC_DIR, "sys_root")

app.secret_key = "A0Zr98j/3yX R~XHH!jmN]LWX/,?RT"


@app.route('/')
def home():
    # request
    return render_template("index.html", title="SysWeb")



from route.fs import *
from route.user import *


if __name__ == '__main__':
    # print(BASE_DIR)
    app.run(debug=True)

