import json
from flask import Blueprint, request, session, jsonify
from ..extensions import db
from ..models.user import User
from ..models.item import Item
from .auth import login_required, _current_user

bp = Blueprint("items", __name__)


@bp.route("", methods=["GET"])
def list_items():
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, int(request.args.get("per_page", 12)))
    keyword = request.args.get("keyword", "").strip()
    tag = request.args.get("tag", "").strip()
    owner_id = request.args.get("owner_id", type=int)

    q = Item.query.filter(Item.status == Item.STATUS_AVAILABLE)
    if keyword:
        q = q.filter(
            (Item.title.contains(keyword)) | (Item.description.contains(keyword))
        )
    if tag:
        q = q.filter(Item.tags.contains(tag))
    if owner_id:
        q = q.filter(Item.owner_id == owner_id)

    q = q.order_by(Item.created_at.desc())
    pag = q.paginate(page=page, per_page=per_page, error_out=False)
    data = [it.to_dict(include_owner=True) for it in pag.items]
    return jsonify({
        "code": 0,
        "data": data,
        "total": pag.total,
        "page": page,
        "per_page": per_page,
    })


@bp.route("/recommend", methods=["GET"])
def recommend():
    """基于标签匹配的首页推荐流：
    1. 如果用户已登录，则先尝试按用户历史浏览/发布的标签匹配
    2. 否则按期望置换标签与物品标签的交集做粗排
    3. 最终按 created_at 倒序返回
    """
    user = _current_user()
    limit = min(50, int(request.args.get("limit", 20)))

    base = Item.query.filter(Item.status == Item.STATUS_AVAILABLE)

    if user:
        my_tags = set()
        my_items = Item.query.filter_by(owner_id=user.id).all()
        for it in my_items:
            my_tags.update(it.tag_list())
            my_tags.update(it.expected_tag_list())

        if my_tags:
            scored = []
            for it in base.all():
                s = len(set(it.tag_list()) & my_tags)
                s += len(set(it.expected_tag_list()) & my_tags)
                if s > 0:
                    scored.append((s, it))
            scored.sort(key=lambda x: (-x[0], -x[1].created_at.timestamp()))
            items = [it for _, it in scored[:limit]]
            if len(items) < limit:
                extra_ids = {i.id for i in items}
                extras = (
                    base.filter(~Item.id.in_(extra_ids))
                    .order_by(Item.created_at.desc())
                    .limit(limit - len(items))
                    .all()
                )
                items.extend(extras)
            return jsonify({"code": 0, "data": [it.to_dict(include_owner=True) for it in items]})

    items = base.order_by(Item.created_at.desc()).limit(limit).all()
    return jsonify({"code": 0, "data": [it.to_dict(include_owner=True) for it in items]})


@bp.route("/<int:item_id>", methods=["GET"])
def detail(item_id):
    it = Item.query.get_or_404(item_id)
    it.view_count = (it.view_count or 0) + 1
    db.session.commit()
    return jsonify({"code": 0, "data": it.to_dict(include_owner=True)})


@bp.route("", methods=["POST"])
@login_required
def create():
    user = _current_user()
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    images = data.get("images") or []
    tags = data.get("tags") or []
    expectation = (data.get("expectation") or "").strip()
    expected_tags = data.get("expected_tags") or []

    if not title or not description:
        return jsonify({"code": 400, "msg": "标题和描述必填"}), 400

    item = Item(
        owner_id=user.id,
        title=title,
        description=description,
        images=json.dumps(images, ensure_ascii=False) if images else None,
        tags=",".join(tags) if tags else None,
        expectation=expectation or None,
        expected_tags=",".join(expected_tags) if expected_tags else None,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"code": 0, "msg": "发布成功", "data": item.to_dict()})


@bp.route("/<int:item_id>", methods=["PUT"])
@login_required
def update(item_id):
    user = _current_user()
    item = Item.query.get_or_404(item_id)
    if item.owner_id != user.id:
        return jsonify({"code": 403, "msg": "无权限修改"}), 403

    data = request.get_json(silent=True) or {}
    if "title" in data and data["title"].strip():
        item.title = data["title"].strip()
    if "description" in data and data["description"].strip():
        item.description = data["description"].strip()
    if "images" in data:
        item.images = json.dumps(data["images"], ensure_ascii=False) if data["images"] else None
    if "tags" in data:
        item.tags = ",".join(data["tags"]) if data["tags"] else None
    if "expectation" in data:
        item.expectation = data["expectation"].strip() or None
    if "expected_tags" in data:
        item.expected_tags = ",".join(data["expected_tags"]) if data["expected_tags"] else None
    if "status" in data:
        item.status = int(data["status"])

    db.session.commit()
    return jsonify({"code": 0, "msg": "更新成功", "data": item.to_dict()})


@bp.route("/<int:item_id>", methods=["DELETE"])
@login_required
def delete(item_id):
    user = _current_user()
    item = Item.query.get_or_404(item_id)
    if item.owner_id != user.id:
        return jsonify({"code": 403, "msg": "无权限删除"}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({"code": 0, "msg": "已删除"})


@bp.route("/mine", methods=["GET"])
@login_required
def mine():
    user = _current_user()
    items = Item.query.filter_by(owner_id=user.id).order_by(Item.created_at.desc()).all()
    return jsonify({"code": 0, "data": [it.to_dict() for it in items]})
