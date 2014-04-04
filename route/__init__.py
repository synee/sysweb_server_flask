from flask import jsonify


def render_error(message, code=0):
    return jsonify(**{"error": True, "message": message, "code": code})
