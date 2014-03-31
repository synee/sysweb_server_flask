import base64
import hashlib
from orm import Model

__author__ = 'shao'


class User(Model):

    @classmethod
    def find_by_email(cls, email):
        return cls.find_one(email=email)

    @classmethod
    def login(cls, email, password):
        user = cls.find_one(email=email)
        if user is None:
            return None
        else:
            print(user.password)
            print(cls.encrypt(password))
            if user.password == cls.encrypt(password):
                return user
            else:
                return None

    @classmethod
    def encrypt(cls, password):
        md5 = hashlib.md5()
        md5.update("password")
        p = base64.urlsafe_b64encode(md5.hexdigest())
        return p

    class Meta(Model.Meta):
        table = "user"







