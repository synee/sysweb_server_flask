import datetime


def default(obj):
    if isinstance(obj, datetime.datetime):
        result = obj.strftime("%Y-%m-%d %H:%M:%S")
        return result