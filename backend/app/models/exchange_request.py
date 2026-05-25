import json
from datetime import datetime
from ..extensions import db


class ExchangeRequest(db.Model):
    __tablename__ = "exchange_requests"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    item_id = db.Column(db.BigInteger, db.ForeignKey("items.id"), nullable=False)
    requester_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(1000))
    offered_item_ids = db.Column(db.Text)
    status = db.Column(db.SmallInteger, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    item = db.relationship("Item", backref=db.backref("requests", lazy="dynamic"))
    requester = db.relationship("User", foreign_keys=[requester_id],
                                backref=db.backref("sent_requests", lazy="dynamic"))

    STATUS_PENDING = 0
    STATUS_ACCEPTED = 1
    STATUS_REJECTED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_DONE = 4
    STATUS_CANCELED = 5

    def offered_ids_list(self) -> list:
        if not self.offered_item_ids:
            return []
        try:
            return json.loads(self.offered_item_ids)
        except (TypeError, ValueError):
            return []

    def to_dict(self, include_relations: bool = False) -> dict:
        data = {
            "id": self.id,
            "item_id": self.item_id,
            "requester_id": self.requester_id,
            "message": self.message,
            "offered_item_ids": self.offered_ids_list(),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_relations:
            if self.item:
                data["item"] = self.item.to_dict()
            if self.requester:
                data["requester"] = self.requester.to_dict()
        return data
