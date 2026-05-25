import json
from flask import Blueprint, request, session, jsonify
from ..extensions import db
from ..models.user import User
from ..models.item import Item
from ..models.exchange_request import ExchangeRequest
from .auth import login_required, _current_user

bp = Blueprint("exchanges", __name__)


@bp.route("", methods=["POST"])
@login_required
def create_request():
    user = _current_user()
    data = request.get_json(silent=True) or {}
    item_id = data.get("item_id", type=int)
    message = (data.get("message") or "").strip()
    offered = data.get("offered_item_ids") or []

    if not item_id:
        return jsonify({"code": 400, "msg": "缺少 item_id"}), 400

    item = Item.query.get(item_id)
    if not item:
        return jsonify({"code": 404, "msg": "物品不存在"}), 404
    if item.owner_id == user.id:
        return jsonify({"code": 400, "msg": "不能向自己发起置换"}), 400

    req = ExchangeRequest(
        item_id=item.id,
        requester_id=user.id,
        message=message or None,
        offered_item_ids=json.dumps(offered) if offered else None,
        status=ExchangeRequest.STATUS_PENDING,
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({"code": 0, "msg": "请求已发送", "data": req.to_dict()})


@bp.route("/<int:req_id>/accept", methods=["POST"])
@login_required
def accept(req_id):
    user = _current_user()
    req = ExchangeRequest.query.get_or_404(req_id)
    if req.item.owner_id != user.id:
        return jsonify({"code": 403, "msg": "无权限操作"}), 403
    if req.status != ExchangeRequest.STATUS_PENDING:
        return jsonify({"code": 400, "msg": "当前状态不可接受"}), 400

    req.status = ExchangeRequest.STATUS_IN_PROGRESS
    req.item.status = Item.STATUS_TRADING
    db.session.commit()
    return jsonify({"code": 0, "msg": "已接受，置换进行中", "data": req.to_dict()})


@bp.route("/<int:req_id>/reject", methods=["POST"])
@login_required
def reject(req_id):
    user = _current_user()
    req = ExchangeRequest.query.get_or_404(req_id)
    if req.item.owner_id != user.id:
        return jsonify({"code": 403, "msg": "无权限操作"}), 403
    if req.status != ExchangeRequest.STATUS_PENDING:
        return jsonify({"code": 400, "msg": "当前状态不可拒绝"}), 400

    req.status = ExchangeRequest.STATUS_REJECTED
    db.session.commit()
    return jsonify({"code": 0, "msg": "已拒绝", "data": req.to_dict()})


@bp.route("/<int:req_id>/complete", methods=["POST"])
@login_required
def complete(req_id):
    user = _current_user()
    req = ExchangeRequest.query.get_or_404(req_id)
    if req.item.owner_id != user.id and req.requester_id != user.id:
        return jsonify({"code": 403, "msg": "无权限操作"}), 403
    if req.status != ExchangeRequest.STATUS_IN_PROGRESS:
        return jsonify({"code": 400, "msg": "当前状态不可完成"}), 400

    req.status = ExchangeRequest.STATUS_DONE
    req.item.status = Item.STATUS_DONE
    db.session.commit()
    return jsonify({"code": 0, "msg": "置换已完成", "data": req.to_dict()})


@bp.route("/<int:req_id>/cancel", methods=["POST"])
@login_required
def cancel(req_id):
    user = _current_user()
    req = ExchangeRequest.query.get_or_404(req_id)
    if req.requester_id != user.id:
        return jsonify({"code": 403, "msg": "无权限操作"}), 403
    if req.status not in (ExchangeRequest.STATUS_PENDING, ExchangeRequest.STATUS_IN_PROGRESS):
        return jsonify({"code": 400, "msg": "当前状态不可取消"}), 400

    req.status = ExchangeRequest.STATUS_CANCELED
    if req.item.status == Item.STATUS_TRADING:
        req.item.status = Item.STATUS_AVAILABLE
    db.session.commit()
    return jsonify({"code": 0, "msg": "已取消", "data": req.to_dict()})


@bp.route("/received", methods=["GET"])
@login_required
def received():
    """物品所有者查看收到的置换请求"""
    user = _current_user()
    reqs = (
        ExchangeRequest.query
        .join(Item, Item.id == ExchangeRequest.item_id)
        .filter(Item.owner_id == user.id)
        .order_by(ExchangeRequest.created_at.desc())
        .all()
    )
    return jsonify({"code": 0, "data": [r.to_dict(include_relations=True) for r in reqs]})


@bp.route("/sent", methods=["GET"])
@login_required
def sent():
    """查看自己发起的置换请求"""
    user = _current_user()
    reqs = (
        ExchangeRequest.query
        .filter_by(requester_id=user.id)
        .order_by(ExchangeRequest.created_at.desc())
        .all()
    )
    return jsonify({"code": 0, "data": [r.to_dict(include_relations=True) for r in reqs]})


@bp.route("/<int:req_id>", methods=["GET"])
@login_required
def detail(req_id):
    user = _current_user()
    req = ExchangeRequest.query.get_or_404(req_id)
    if req.item.owner_id != user.id and req.requester_id != user.id:
        return jsonify({"code": 403, "msg": "无权限查看"}), 403
    return jsonify({"code": 0, "data": req.to_dict(include_relations=True)})
