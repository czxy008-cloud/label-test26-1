import json
from datetime import datetime
from ..extensions import db


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.Text)
    tags = db.Column(db.String(500))
    expectation = db.Column(db.String(500))
    expected_tags = db.Column(db.String(500))
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    view_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("User", backref=db.backref("items", lazy="dynamic"))

    STATUS_AVAILABLE = 1
    STATUS_TRADING = 2
    STATUS_DONE = 3
    STATUS_OFFLINE = 4

    def image_list(self) -> list:
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except (TypeError, ValueError):
            return [self.images]

    def tag_list(self) -> list:
        return [t.strip() for t in (self.tags or "").split(",") if t.strip()]

    def expected_tag_list(self) -> list:
        return [t.strip() for t in (self.expected_tags or "").split(",") if t.strip()]

    def to_dict(self, include_owner: bool = False) -> dict:
        data = {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "description": self.description,
            "images": self.image_list(),
            "tags": self.tag_list(),
            "expectation": self.expectation,
            "expected_tags": self.expected_tag_list(),
            "status": self.status,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_owner and self.owner:
            data["owner"] = self.owner.to_dict()
        return data
