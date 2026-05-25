import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from .auth import login_required, _current_user

bp = Blueprint("uploads", __name__)


def _allowed(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@bp.route("", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"code": 400, "msg": "未找到文件"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"code": 400, "msg": "文件为空"}), 400
    if not _allowed(f.filename):
        return jsonify({"code": 400, "msg": "不支持的文件类型"}), 400

    ext = f.filename.rsplit(".", 1)[-1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    f.save(save_path)

    url = f"/api/uploads/{name}"
    return jsonify({"code": 0, "data": {"url": url, "filename": name}})


@bp.route("/<path:filename>", methods=["GET"])
def serve(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
