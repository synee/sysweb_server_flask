import base64
import hashlib
import json
import datetime
import orm
from orm.user import User

# for item in orm.execute("SELECT * FROM user WHERE id=  %d" % (22,)):
#     print(type(item["date_created"]))
from sson import json_util

# print(User.find_by_id(22).username)
#
print User.login(email="th.synee@gmail.com", password="password")

# print(json.dumps({
#     "Hello": "World",
#     "now": datetime.datetime.now()
# }, default=json_util.default))


# print("//s//sdfg//sdfg/sdfg/er".replace("//", "/", 1))
# print(({"Hello": "World"}).keys())

u = User(
    id=40,
    username="postmaster@abillist.com",
    email="postmaster@abillist.com",
    password="password",
    code="asdfawer543rfaeee")

print(u.save())