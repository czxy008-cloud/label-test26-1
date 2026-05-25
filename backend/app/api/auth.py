from flask import Blueprint, request, session, jsonify
from ..extensions import db
from ..models.user import User

bp = Blueprint("auth", __name__)


def _current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)


def login_required(view):
    from functools import wraps

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"code": 401, "msg": "请先登录"}), 401
        return view(*args, **kwargs)

    return wrapper


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    nickname = (data.get("nickname") or "").strip() or username

    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空"}), 400
    if len(username) < 3 or len(username) > 50:
        return jsonify({"code": 400, "msg": "用户名长度 3-50"}), 400
    if len(password) < 6:
        return jsonify({"code": 400, "msg": "密码至少 6 位"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"code": 400, "msg": "用户名已存在"}), 400

    user = User(username=username, nickname=nickname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"code": 0, "msg": "注册成功", "data": user.to_dict()})


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401

    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return jsonify({"code": 0, "msg": "登录成功", "data": user.to_dict()})


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"code": 0, "msg": "已退出登录"})


@bp.route("/me", methods=["GET"])
def me():
    user = _current_user()
    if not user:
        return jsonify({"code": 401, "msg": "未登录"}), 401
    return jsonify({"code": 0, "data": user.to_dict()})
