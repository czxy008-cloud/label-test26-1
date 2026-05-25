from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User
from ..models.message import Message
from .auth import login_required, _current_user

bp = Blueprint("messages", __name__)


@bp.route("/conversations", methods=["GET"])
@login_required
def conversations():
    """获取当前用户的所有会话（按对方分组，取最近一条消息）"""
    user = _current_user()
    uid = user.id

    pairs = (
        db.session.query(
            db.func.greatest(Message.sender_id, Message.receiver_id).label("a"),
            db.func.least(Message.sender_id, Message.receiver_id).label("b"),
            db.func.max(Message.created_at).label("last_at"),
        )
        .filter((Message.sender_id == uid) | (Message.receiver_id == uid))
        .group_by("a", "b")
        .order_by(db.desc("last_at"))
        .all()
    )

    result = []
    for a, b, last_at in pairs:
        other_id = b if a == uid else a
        other = User.query.get(other_id)
        last_msg = (
            Message.query
            .filter(
                ((Message.sender_id == uid) & (Message.receiver_id == other_id))
                | ((Message.sender_id == other_id) & (Message.receiver_id == uid))
            )
            .order_by(Message.created_at.desc())
            .first()
        )
        unread = (
            Message.query
            .filter_by(sender_id=other_id, receiver_id=uid, is_read=False)
            .count()
        )
        result.append({
            "other": other.to_dict() if other else None,
            "last_message": last_msg.to_dict() if last_msg else None,
            "unread_count": unread,
            "last_at": last_at.isoformat() if last_at else None,
        })
    return jsonify({"code": 0, "data": result})


@bp.route("/<int:other_id>", methods=["GET"])
@login_required
def history(other_id):
    user = _current_user()
    uid = user.id
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(100, int(request.args.get("per_page", 50)))

    q = Message.query.filter(
        ((Message.sender_id == uid) & (Message.receiver_id == other_id))
        | ((Message.sender_id == other_id) & (Message.receiver_id == uid))
    ).order_by(Message.created_at.desc())

    pag = q.paginate(page=page, per_page=per_page, error_out=False)
    messages = [m.to_dict() for m in pag.items]
    messages.reverse()

    Message.query.filter_by(sender_id=other_id, receiver_id=uid, is_read=False).update(
        {"is_read": True}, synchronize_session=False
    )
    db.session.commit()

    return jsonify({
        "code": 0,
        "data": messages,
        "total": pag.total,
        "page": page,
    })


@bp.route("", methods=["POST"])
@login_required
def send():
    user = _current_user()
    data = request.get_json(silent=True) or {}
    receiver_id = data.get("receiver_id", type=int)
    content = (data.get("content") or "").strip()

    if not receiver_id or not content:
        return jsonify({"code": 400, "msg": "接收者和内容必填"}), 400
    if receiver_id == user.id:
        return jsonify({"code": 400, "msg": "不能给自己发消息"}), 400
    if not User.query.get(receiver_id):
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    msg = Message(sender_id=user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.commit()

    from ..extensions import socketio
    socketio.emit("new_message", msg.to_dict(), to=f"user_{receiver_id}")
    socketio.emit("new_message", msg.to_dict(), to=f"user_{user.id}")

    return jsonify({"code": 0, "msg": "发送成功", "data": msg.to_dict()})
